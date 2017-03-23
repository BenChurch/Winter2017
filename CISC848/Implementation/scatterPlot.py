import numpy as np
#import pylab as pl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv

DataDir = './/Data//'
ExploitedCsv = 'ExploitedIdsVectors.csv'
UnexploitedCsv = 'UnexploitedIdsVectors.csv'
Classes = ['Exploited', 'Not Exploited']
ClassColors = ['r', 'b']
ExploitedScores = []
OptExploitedScores = []
UnexploitedScores = []
OptUnexploitedScores = []

OriginalParameters = [0.395, 0.646, 1.0, 0.35, 0.61, 0.71, 0.45, 0.56, 0.704, 0, 0.275, 0.66, 0, 0.275, 0.66, 0, 0.275, 0.66]
OptimizedParameters = []

def Vector2BaseScore(Vector, Params): 
  # Expecting a 6 element array of chars indicating base score metric values
  # Expecting 6 3D arrays in ParamSets = [avParams, acParams, auParams, confParams, integParams = [1,2,3], availParams]
  # Explicitly list hard-coded equation parameters
  
  HardParams = [0.6, 0.4, 1.5, 10.41, 20, 0, 1.176]
  
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
 
with open('optimizationResults.csv') as f:
  r = csv.reader(f, quotechar=None)
  for line in r:
    if line[0] == "Optimized":
      OptimizedParameters.append(float(line[1][2:]))
      OptimizedParameters.append(float(line[2]))
      OptimizedParameters.append(float(line[3]))
      OptimizedParameters.append(float(line[4]))
      OptimizedParameters.append(float(line[5]))
      OptimizedParameters.append(float(line[6]))
      OptimizedParameters.append(float(line[7]))
      OptimizedParameters.append(float(line[8]))
      OptimizedParameters.append(float(line[9]))
      OptimizedParameters.append(float(line[10]))
      OptimizedParameters.append(float(line[11]))
      OptimizedParameters.append(float(line[12]))
      OptimizedParameters.append(float(line[13]))
      OptimizedParameters.append(float(line[14]))
      OptimizedParameters.append(float(line[15]))
      OptimizedParameters.append(float(line[16]))
      OptimizedParameters.append(float(line[17]))
      OptimizedParameters.append(float(line[18][:-2]))
      print(OptimizedParameters)
 
with open(DataDir + ExploitedCsv, encoding='utf-8') as f:
  r = csv.reader(f, quotechar = None)
  for line in r:
    CurrentVector = line[1]
    CurrentScore = Vector2BaseScore(CurrentVector, OriginalParameters)
    ExploitedScores.append(CurrentScore)
    OptScore = Vector2BaseScore(CurrentVector, OptimizedParameters)
    OptExploitedScores.append(OptScore)
      
with open(DataDir + UnexploitedCsv, encoding='utf-8') as f:
  r = csv.reader(f, quotechar = None)
  for line in r:
    CurrentVector = line[1]
    CurrentScore = Vector2BaseScore(CurrentVector, OriginalParameters)
    OptScore = Vector2BaseScore(CurrentVector, OptimizedParameters)
    UnexploitedScores.append(CurrentScore) 
    OptUnexploitedScores.append(OptScore)
 
# Find max and min score to renormalize
maxScore = 10
minScore = 0
for Score in OptExploitedScores + OptUnexploitedScores:
  if Score > maxScore: 
    maxScore = Score
    continue
  if Score < minScore:
    minScore = Score
    continue
    
# Renormalize
for i, Score in enumerate(OptExploitedScores):
  OptExploitedScores[i] = (Score + minScore) / ((maxScore - minScore) / 10.0)
for i, Score in enumerate(OptUnexploitedScores):
  OptUnexploitedScores[i] = (Score + minScore) / ((maxScore - minScore) / 10.0)
  

""" 
Exp = plt.scatter(np.ones(len(ExploitedScores)), ExploitedScores, s=10)
Unexp = plt.scatter(np.zeros(len(UnexploitedScores)), UnexploitedScores, s=10)
plt.axis([-0.5, 1.5, 0, 12])
xTickLabels = ['', '', 'No', '', '', '', 'Yes', '', '']
yTickLabels = ['0', '2', '4', '6', '8', '10', '']
ax = plt.axes()
ax.set_ylabel('Base score')
ax.set_xlabel('Exploited?')
ax.set_xticklabels(xTickLabels)
ax.set_yticklabels(yTickLabels)
plt.title('Exploitation vs. Base Score')
plt.show()
#Fig = plt.gcf()
"""

Fig = plt.figure()
MeanLine = np.linspace(-0.5, 1.5, 1000)
plt.boxplot([OptUnexploitedScores, OptExploitedScores], [0, 1], widths = 0.6)
#Unexp = plt.scatter(np.ones(len(UnexploitedScores)), UnexploitedScores, s=15, lw = 1, marker='x')
#Exp = plt.scatter(2*np.ones(len(ExploitedScores)), ExploitedScores, s=15, lw = 1, marker='x')
#plt.plot(MeanScore * np.ones(len(MeanLine)), MeanLine)
plt.title('Exploits vs. Base Score')
#plt.boxplot([ExploitedScores, [2], widths = 0.6)
ax = plt.axes()
ax.set_xticklabels(['No', 'Yes'])
ax.set_xlabel('Exploited?')
ax.set_ylabel('Base score')
plt.show()

