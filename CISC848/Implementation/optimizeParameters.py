import csv
import numpy as np
from scipy.optimize import minimize
import vectors2metrics as v2m

VulnDir = './/Data//'
UnexploitedCsvFile = 'UnexploitedIdsVectors.csv'
ExploitedCsvFile = 'ExploitedIdsVectors.csv'

OutputDir = './/'
OutputFile = 'optimizationResults.csv'

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
   
SearchSpaceStart = [0.395, 0.646, 1.0, 0.35, 0.61, 0.71, 0.45, 0.56, 0.704, 0, 0.275, 0.66, 0, 0.275, 0.66, 0, 0.275, 0.66]
OriginalICC = v2m.ComputeICC(SearchSpaceStart, Unexploited, Exploited)
  # Corresponds to [avParams, acParams, auParams, confParams, integParams, availParams]
Bounds = []
for Param in enumerate(SearchSpaceStart):
  Bounds.append([0.0, 1.0])
  
def OptObjFun(Params, Unexpl, Expl):
  return 1 - v2m.ComputeICC(Params, Unexpl, Expl)
  
result = (minimize(OptObjFun, SearchSpaceStart, (Unexploited, Exploited), 'SLSQP', None, None, None, Bounds))
OptParams = result.x
OptICC = v2m.ComputeICC(OptParams, Unexploited, Exploited)

OptParamsStr = str(OptParams)

print(OptParamsStr)

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
    
    
  
with open(OutputDir + OutputFile, 'w', newline='') as file:
  outputWriter = csv.writer(file)
  outputWriter.writerow(['Parameter Set', 'Parameters', 'ICC'])
  outputWriter.writerow(['Original', SearchSpaceStart, OriginalICC])
  outputWriter.writerow(['Optimized', OptParamsArray, OptICC])