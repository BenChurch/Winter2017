import csv
PredictionsDir = 'C:\\Users\\church\\Documents\\Winter2017\\MICCAI2017\\Data\\'
PredictionFiles = ['PredictSupAntR','PredictSupAntA','PredictSupAntS', 'PredictInfAntR','PredictInfAntA','PredictInfAntS']
NetworkInputDir = 'C:\\Users\\church\\Documents\\Winter2017\\MICCAI2017\\Data\\'    # Look through this to see which markupsNodes the given prediction corresponds to
NetworkInputFile = 'NetworkInput.csv'
NodeOrder = []
with open(NetworkInputDir + NetworkInputFile, 'rb') as NetworkInput:
  NetworkInputReader = csv.reader(NetworkInput, delimiter = ',')
  for row in NetworkInputReader:
    NodeOrder.append(row[-1][:-6])

SupScalePointsR = []
SupScalePointsA = []
SupScalePointsS = []
InfScalePointsR = []
InfScalePointsA = []
InfScalePointsS = []

with open(PredictionsDir + PredictionFiles[0] + '.csv', 'rb') as InputFile:
  InputReader = csv.reader(InputFile, delimiter = ',')
  for row in InputReader:
    SupScalePointsR.append(row[0])

with open(PredictionsDir + PredictionFiles[1] + '.csv', 'rb') as InputFile:
  InputReader = csv.reader(InputFile, delimiter = ',')
  for row in InputReader:
    SupScalePointsA.append(row[0])

with open(PredictionsDir + PredictionFiles[2] + '.csv', 'rb') as InputFile:
  InputReader = csv.reader(InputFile, delimiter = ',')
  for row in InputReader:
    SupScalePointsS.append(row[0])

with open(PredictionsDir + PredictionFiles[3] + '.csv', 'rb') as InputFile:
  InputReader = csv.reader(InputFile, delimiter = ',')
  for row in InputReader:
    InfScalePointsR.append(row[0])

with open(PredictionsDir + PredictionFiles[4] + '.csv', 'rb') as InputFile:
  InputReader = csv.reader(InputFile, delimiter = ',')
  for row in InputReader:
    InfScalePointsA.append(row[0])

with open(PredictionsDir + PredictionFiles[5] + '.csv', 'rb') as InputFile:
  InputReader = csv.reader(InputFile, delimiter = ',')
  for row in InputReader:
    InfScalePointsS.append(row[0])

for i, (R,A,S) in enumerate(zip(SupScalePointsR[1:], SupScalePointsA[1:], SupScalePointsS[1:])):
  CurrentNode = slicer.util.getNode(NodeOrder[i+1])
  CurrentNode.AddFiducial(float(R), float(A), float(S))
  CurrentNode.SetNthFiducialLabel(CurrentNode.GetNumberOfFiducials(), 'SupScalePoint_' + str(i))

for i, (R,A,S) in enumerate(zip(InfScalePointsR[1:], InfScalePointsA[1:], InfScalePointsS[1:])):
  CurrentNode = slicer.util.getNode(NodeOrder[i+1])
  CurrentNode.AddFiducial(float(R) ,float(A), float(S))
  CurrentNode.SetNthFiducialLabel(CurrentNode.GetNumberOfFiducials(), 'InfScalePoint_' + str(i))
