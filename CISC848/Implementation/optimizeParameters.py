import csv
import numpy as np
from scipy.optimize import minimize
import vectors2metrics as v2m

VulnDir = './/Data//'
UnexploitedCsvFile = 'UnexploitedIdsVectors.csv'
ExploitedCsvFile = 'ExploitedIdsVectors.csv'

OutputDir = './/'
OutputFile = 'optimizationResults.csv'

ClassificationThreshold = 7
    
SearchSpaceStart = [0.395, 0.646, 1.0, 0.35, 0.61, 0.71, 0.45, 0.56, 0.704, 0, 0.275, 0.66, 0, 0.275, 0.66, 0, 0.275, 0.66]
  
def ReadInData():
  # Read in Ids and vectors
  Unexploited = []
  with open(VulnDir + UnexploitedCsvFile, 'r', encoding='ascii', errors="surrogateescape") as file:
    EntryReader = csv.reader(file)
    for line in EntryReader:
      Unexploited.append((line[0], line[1]))  # (ID, Vector)
         
  Exploited = []
  with open(VulnDir + ExploitedCsvFile, 'r', encoding='ascii', errors="surrogateescape") as file:
    EntryReader = csv.reader(file)
    for line in EntryReader:
      Exploited.append((line[0], line[1]))  # (ID, Vector)
      
  return (Unexploited, Exploited)

def WriteOutData(Unexpl, Expl, OptParamsStr, Threshold):
  OriginalConfusionMatrix = v2m.PredictExploits(Unexpl, Expl, SearchSpaceStart, Threshold)
  OriginalRiskReduction = (OriginalConfusionMatrix[0][0] / (OriginalConfusionMatrix[0][0] + OriginalConfusionMatrix[0][1])) - (OriginalConfusionMatrix[1][0] / (OriginalConfusionMatrix[1][0] + OriginalConfusionMatrix[1][1]))
  
  OptParamsArray = []
  ParamStart = 0
  ParamStop = 0
  for i, char in enumerate(OptParamsStr, start = ParamStart):
    if char == '.':
      ParamStart = i-1
      if OptParamsStr[ParamStart:].__contains__(' '):
        ParamStop = OptParamsStr[ParamStart:].index(' ') + ParamStart
      else: ParamStop = OptParamsStr[ParamStart:].index(']') + ParamStart
      OptParamsArray.append(float(OptParamsStr[ParamStart:ParamStop]))
  OptConfusionMatrix = v2m.PredictExploits(Unexpl, Expl, OptParamsArray, Threshold)
  OptRiskReduction =   (OptConfusionMatrix[0][0] / (OptConfusionMatrix[0][0] + OptConfusionMatrix[0][1])) - (OptConfusionMatrix[1][0] / (OptConfusionMatrix[1][0] + OptConfusionMatrix[1][1]))
  
  with open(OutputDir + OutputFile, 'w', newline='') as file:
    outputWriter = csv.writer(file)
    outputWriter.writerow(['Parameter Set', 'ConfusionMatrix', 'Risk reduction', 'Sensitivity', 'Precision', 'Unexpl ICC', 'Expl ICC', 'Parameters'])
    outputWriter.writerow(['Original', OriginalConfusionMatrix, OriginalRiskReduction, v2m.ComputeSensitivity(OriginalConfusionMatrix), v2m.ComputePrecision(OriginalConfusionMatrix), OriginalICCs[0], OriginalICCs[1]] + SearchSpaceStart)
    outputWriter.writerow(['Optimized', OptConfusionMatrix, OptRiskReduction, v2m.ComputeSensitivity(OptConfusionMatrix), v2m.ComputePrecision(OptConfusionMatrix), OptICCs[0], OptICCs[1]] + OptParamsArray)

def OptObjFun(Params, Unexpl, Expl, Threshold):
  
  Beta = 3.0
  ConfusionMatrix = v2m.PredictExploits(Unexpl, Expl, Params, Threshold)
  
  ICCs = v2m.ComputeICC(Params, Unexpl, Expl)
  CompICC = (ICCs[0] + ICCs[1]*3) / 4.0
  
  MeanOverpredictionError = v2m.ComputeMeanOverpredictionError(Unexpl, Params, Threshold)
  UnitOverpredictionError = MeanOverpredictionError / (10.0 - Threshold)
  MeanUnderpredictionError = v2m.ComputeMeanUnderpredictionError(Expl, Params, Threshold)
  UnitUnderpredictionError = MeanUnderpredictionError / (Threshold)
  
  Sensitivity = v2m.ComputeSensitivity(ConfusionMatrix)
  Precision = v2m.ComputePrecision(ConfusionMatrix)
  F1 = ((1.0 - Precision) + (UnitOverpredictionError)) / 2.0
  F2 = ((1.0 - Sensitivity) + (UnitUnderpredictionError)) / 2.0
  Fmeasure = (3*F1 + F2) / 4.0
  RiskReduction = (ConfusionMatrix[0][0] / (ConfusionMatrix[0][0] + ConfusionMatrix[0][1])) - (ConfusionMatrix[1][0] / (ConfusionMatrix[1][0] + ConfusionMatrix[1][1]))
  #Fmeasure = ((1 - RiskReduction) + (UnitUnderpredictionError)) / 2.0
  #Fmeasure = 1 - CompICC
  print("Optimization objective function value: " + str(Fmeasure))
  return (Fmeasure)
  
(Unexploited, Exploited) = ReadInData()


OriginalICCs = v2m.ComputeICC(SearchSpaceStart, Unexploited, Exploited)

Bounds = []
for Param in enumerate(SearchSpaceStart):
  Bounds.append([0.0, 1.0])
  
result = (minimize(OptObjFun, SearchSpaceStart, (Unexploited, Exploited, ClassificationThreshold), 'SLSQP', None, None, None, Bounds))
OptParams = result.x
OptICCs = v2m.ComputeICC(OptParams, Unexploited, Exploited)

OptParamsStr = str(OptParams)

print(OptParamsStr)

WriteOutData(Unexploited, Exploited, OptParamsStr, ClassificationThreshold)

