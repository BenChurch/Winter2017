import csv
import numpy as np
from scipy.optimize import minimize

# Base score threshold for positive exploit prediction
#PredictionThreshold = 7.5

VulnDir = './/Data//'
UnexploitedCsvFile = 'UnexploitedIdsVectors.csv'
ExploitedCsvFile = 'ExploitedIdsVectors.csv'

ParamsDir = './/'
ParamsFile = 'optimizationResults.csv'
RowRange = range(1, 3) # Allow some kind of hyper-parameter search
NumParams = 18  # How many parameters to read from each row

"""
OutputDir = './/'
OutputFile = 'Metrics.csv'
"""

OriginalParameters = [0.395, 0.646, 1.0, 0.35, 0.61, 0.71, 0.45, 0.56, 0.704, 0, 0.275, 0.66, 0, 0.275, 0.66, 0, 0.275, 0.66]

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

def Vector2BaseScore(Vector, Params): 
  # Expecting 6 3D arrays in ParamSets = [avParams, acParams, auParams, confParams, integParams = [1,2,3], availParams]
  
  # Some vectors are of a different form entirely, useless for this method, return MAGIC 5 for now
  if Vector[0] == "V":  
    return 5
  
  if Vector[3] == "L": AccessVector = Params[0]
  elif Vector[3] == "A": AccessVector = Params[1]
  elif Vector[3] == "N": AccessVector = Params[2]
  
  if Vector[8] == "H": AccessComplexity = Params[3]
  elif Vector[8] == "M": AccessComplexity = Params[4]
  elif Vector[8] == "L": AccessComplexity = Params[5]
  
  if Vector[13] == "M": Authentication = Params[6]
  elif Vector[13] == "S": Authentication = Params[7]
  elif Vector[13] == "N": Authentication = Params[8]
  
  if Vector[17] == "N": ConfImpact = Params[9]
  elif Vector[17] == "P": ConfImpact = Params[10]
  elif Vector[17] == "C": ConfImpact = Params[11]
  
  if Vector[21] == "N": IntegImpact = Params[12]
  elif Vector[21] == "P": IntegImpact = Params[13]
  elif Vector[21] == "C": IntegImpact = Params[14]

  if Vector[25] == "N": AvailImpact = Params[15]
  elif Vector[25] == "P": AvailImpact = Params[16]
  elif Vector[25] == "C": AvailImpact = Params[17]
  
  Exploitability = 20* AccessVector*AccessComplexity*Authentication
  
  Impact = 10.41*(1-(1-ConfImpact)*(1-IntegImpact)*(1-AvailImpact))
  if Impact == 0:
    Fimpact = 0
  else:
    Fimpact = 1.176
  
  BaseScore = ((0.6*Impact)+(0.4*Exploitability)-1.5)*Fimpact
  
  return BaseScore
  
def ComputeICC(Params, Unexpl, Expl):
  UnexploitedScores = []
  SumScores = 0
  for Vuln in Unexpl:
    #print(Vuln)
    Score = Vector2BaseScore(Vuln[1], Params)
    UnexploitedScores.append(Score)
    SumScores += Score
  MeanUnexplScore = SumScores / len(Unexpl)
  
  ExploitedScores = []
  SumScores = 0
  for Vuln in Expl:
    Score = Vector2BaseScore(Vuln[1], Params)
    ExploitedScores.append(Vector2BaseScore(Vuln[1], Params))
    SumScores += Score
  MeanExplScore = SumScores / len(Expl)
  
  GrandMean = ((MeanUnexplScore * len(Unexpl)) + (MeanExplScore * len(Expl)) ) / (len(Unexpl) + len(Expl))
  
  # Compute sum squares and mean sum squares for intra class variability
  SSintraUnexpl = 0
  for Score in UnexploitedScores:
    SSintraUnexpl += (Score - MeanUnexplScore) ** 2
  MSSintraUnexpl = SSintraUnexpl / (len(Unexpl) - 1)
  
  SSintraExpl = 0
  for Score in ExploitedScores:
    SSintraExpl += (Score - MeanExplScore) ** 2
  MSSintraExpl = SSintraExpl / (len(Expl) - 1)
  
  # Compute sum squares and mean sum squares for class - universe variability  --- want to maximize this wrt intra variabilities
  SSextraUnexpl = 0
  for Score in UnexploitedScores:
    SSextraUnexpl += (Score - GrandMean) ** 2
  MSSextraUnexpl = SSextraUnexpl / (len(Unexpl) - 1)
  
  SSextraExpl = 0
  for Score in ExploitedScores:
    SSextraExpl += (Score - GrandMean) ** 2
  MSSextraExpl = SSextraExpl / (len(Expl) - 1)
  
  #ICCs = ((MSSextraExpl / (MSSextraExpl + MSSintraExpl)), (MSSextraUnexpl / (MSSextraUnexpl + MSSintraUnexpl)))

  ICCExpl = MSSextraExpl / (MSSextraExpl + MSSintraExpl)
  ICCUnexpl = MSSextraUnexpl / (MSSextraUnexpl + MSSintraUnexpl)
  return (ICCUnexpl, ICCExpl)
  
def PredictExploits(Unexploited, Exploited, Params, Threshold):       # Combines all vuln vectors and computes their base score using Params. Scores > Threshold mean positive prediction
  # Returns confusion matrix [[TP, FP], [FN, TN]]
  
  # First, compute all scores since they must be renormalized
  MaxScore = 10
  MinScore = 10
  UnexplScores = []
  for Vuln in Unexploited:
    Score = Vector2BaseScore(Vuln[1], Params)
    UnexplScores.append(Score)
    if Score > MaxScore: MaxScore = Score
    if Score < MinScore: MinScore = Score
    
  ExplScores = []
  for Vuln in Exploited:
    Score = Vector2BaseScore(Vuln[1], Params)
    ExplScores.append(Score)
    if Score > MaxScore: MaxScore = Score
    if Score < MinScore: MinScore = Score
  
  if MinScore < 0:
    for VulnScore in UnexplScores:
      VulnScore -= MinScore
    for VulnScore in ExplScores:
      VulnScore -= MinScore
  # ASSERT that min score is now 0
  
  for VulnScore in UnexplScores:
    VulnScore = (VulnScore / MaxScore) * 10
    
  for VulnScore in ExplScores:
    VulnScore = (VulnScore / MaxScore) * 10
  
  # ASSERT that max score is now 10
  
  TN = 0
  FP = 0
  for VulnScore in UnexplScores:
    #print(VulnScore)
    if VulnScore >= Threshold: FP += 1
    else: TN += 1
    
  TP = 0
  FN = 0
  for VulnScore in ExplScores:
    #print(VulnScore)
    if VulnScore >= Threshold: TP += 1
    else: FN += 1
    
  return [[TP, FP], [FN, TN]]
  
def ComputeSensitivity(ConfusionMatrix):
  TPs = float(ConfusionMatrix[0][0])
  FNs = float(ConfusionMatrix[1][0])
  return (TPs / (TPs + FNs))

def ComputePrecision(ConfusionMatrix):
  TPs = float(ConfusionMatrix[0][0])
  FPs = float(ConfusionMatrix[0][1])
  if TPs + FPs == 0: 
    return 0
  else:
    return (TPs / (TPs + FPs))
  
# Overprediction and Underprediction errors provide better resolution for optimization objective function than binary classification based Sensitivity and Precision
def ComputeMeanOverpredictionError(Unexploited, Params, Threshold):
  # First, normalize scores to all be less than 10
  MaxScore = 10
  UnnormalizedScores = []
  for Vuln in Unexploited:
    Score = Vector2BaseScore(Vuln[1], Params)
    UnnormalizedScores.append(Score)
    if MaxScore < Score:
      MaxScore = Score
  
  NormalizedScores = []
  for UnnormalizedScore in UnnormalizedScores:
    NormalizedScores.append((UnnormalizedScore / MaxScore) * 10.0)
  
  SumOverpredictionError = 0
  for Score in NormalizedScores:
    if Score > Threshold:
      SumOverpredictionError += Score - Threshold
    # else: OverpredictionError = 0
  MeanOverpredictionError = SumOverpredictionError / len(Unexploited)
  return MeanOverpredictionError
  
def ComputeMeanUnderpredictionError(Exploited, Params, Threshold):
  SumUnderpredictionError = 0
  for Vuln in Exploited:
    Score = Vector2BaseScore(Vuln[1], Params)
    if Score < Threshold:
      SumUnderpredictionError += Threshold - Score
    #else: Underprediction = 0
  MeanUnderpredictionError = SumUnderpredictionError / len(Exploited)
  return MeanUnderpredictionError