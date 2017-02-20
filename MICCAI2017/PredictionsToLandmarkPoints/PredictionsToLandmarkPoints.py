import csv
#PredictionsDir = 'C:\\Users\\church\\Documents\\Winter2017\\MICCAI2017\\Data\\'
PredictionsDir = 'C:\\Users\\Ben\\Documents\\Masters16_17\\Winter2017\\MICCAI2017\\Data\\'
PredictionFiles = ['PredictSupAntR','PredictSupAntA','PredictSupAntS', 'PredictInfAntR','PredictInfAntA','PredictInfAntS']
NetworkInputDir = 'C:\\Users\\Ben\\Documents\\Masters16_17\\Winter2017\\MICCAI2017\\Data\\'    # Look through this to see which markupsNodes the given prediction corresponds to
#NetworkInputDir = 'C:\\Users\\church\\Documents\\Winter2017\\MICCAI2017\\Data\\'
NetworkInputFile = 'NetworkInput.csv'

# Nodes not organizaed by increasing patient number in NetworkInput, must add predicted scale points in their existing order
NodeOrder = []
with open(NetworkInputDir + NetworkInputFile, 'rb') as NetworkInput:
  NetworkInputReader = csv.reader(NetworkInput, delimiter = ',')
  for i, row in enumerate(NetworkInputReader):
    if i == 0:    # i > 0 because header row
      continue
    if i == 1:  
      NodeOrder.append(row[-1][:-6])
      continue
    if NodeOrder[-1] == row[-1][:-6]:   # Eliminates multiplicity for creating ScalePointsNodes
      continue
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

# Delete header rows
SupScalePointsR.__delitem__(0)
SupScalePointsA.__delitem__(0)
SupScalePointsS.__delitem__(0)
InfScalePointsR.__delitem__(0)
InfScalePointsA.__delitem__(0)
InfScalePointsS.__delitem__(0)

SupAndInfPoint = zip(zip(SupScalePointsR, SupScalePointsA, SupScalePointsS), zip(InfScalePointsR, InfScalePointsA, InfScalePointsS))
RowCounter = 0
for NewNode in range(len(NodeOrder)):
  ScalePointsNode = slicer.vtkMRMLMarkupsFiducialNode()
  ScalePointsNode.SetName("ScalePoints" + NodeOrder[NewNode][-3:])
  slicer.mrmlScene.AddNode(ScalePointsNode)
  CorrespondingLandmarksNode = slicer.util.getNode(NodeOrder[NewNode])
  for CorrespondingPoint in range(0, CorrespondingLandmarksNode.GetNumberOfFiducials(), 2):
    #CurrentIndex = (NewNode * (CorrespondingPoint)) + (CorrespondingPoint % CorrespondingLandmarksNode.GetNumberOfFiducials())
    ScalePointsNode.AddFiducialFromArray([float(SupAndInfPoint[RowCounter][0][0]), float(SupAndInfPoint[RowCounter][0][1]), float(SupAndInfPoint[RowCounter][0][2])])
    ScalePointsNode.SetNthFiducialLabel(ScalePointsNode.GetNumberOfFiducials()-1, CorrespondingLandmarksNode.GetNthFiducialLabel(CorrespondingPoint)[:-1] + "S")
    ScalePointsNode.AddFiducialFromArray([float(SupAndInfPoint[RowCounter][1][0]), float(SupAndInfPoint[RowCounter][1][1]), float(SupAndInfPoint[RowCounter][1][2])])
    ScalePointsNode.SetNthFiducialLabel(ScalePointsNode.GetNumberOfFiducials()-1, CorrespondingLandmarksNode.GetNthFiducialLabel(CorrespondingPoint+1)[:-1] + "I")
    RowCounter += 1

#ScalePointCoords = (zip(zip(SupScalePointsR[1:], SupScalePointsA[1:], SupScalePointsS[1:]), zip(InfScalePointsR[1:], InfScalePointsA[1:], InfScalePointsS[1:])))  # Of the form ((Rs,As,Ss), (Ri, Ai, Si))
#print ScalePointCoords
for NewNode in range(len(NodeOrder)):
  ScalePointsNode = slicer.vtkMRMLMarkupsFiducialNode()
  ScalePointsNode.SetName("ScalePoints" + NodeOrder[NewNode][-3:])
  slicer.mrmlScene.AddNode(ScalePointsNode)
  CorrespondingLandmarksNode = slicer.util.getNode(NodeOrder[NewNode])
  for CorrespondingPoint in range(0, CorrespondingLandmarksNode.GetNumberOfFiducials()):
    ScalePointIndex = (NewNode * (CorrespondingPoint + 1)) + CorrespondingPoint
    ScalePointsNode.AddFiducialFromArray([float(SupScalePointsR[ScalePointIndex]), float(SupScalePointsA[ScalePointIndex]), float(SupScalePointsS[ScalePointIndex])])
    ScalePointsNode.SetNthFiducialLabel(ScalePointIndex, CorrespondingLandmarksNode.GetNthFiducialLabel(ScalePointIndex)[:-1] + "S")
    ScalePointsNode.AddFiducialFromArray([float(InfScalePointsR[ScalePointIndex]), float(InfScalePointsA[ScalePointIndex]), float(InfScalePointsS[ScalePointIndex])])
    ScalePointsNode.SetNthFiducialLabel(ScalePointIndex+1, CorrespondingLandmarksNode.GetNthFiducialLabel(ScalePointIndex + 1)[:-1] + "I")

for i, LandmarksNode in enumerate(NodeOrder):
  CorrespondingLandmarksNode = slicer.util.getNode(LandmarksNode)
  ScalePointsNode = slicer.util.getNode("ScalePoints" + NodeOrder[i][-3:])
  for P in range(0, CorrespondingLandmarksNode.GetNumberOfFiducials(), 2):
    
    
  
for i, ((Rs,As,Ss), (Ri, Ai, Si)) in enumerate(zip(zip(SupScalePointsR[1:], SupScalePointsA[1:], SupScalePointsS[1:]), zip(InfScalePointsR[1:], InfScalePointsA[1:], InfScalePointsS[1:]))):
  CorrespondingLandmarksNode = slicer.util.getNode(NodeOrder[i])
  ScalePointsNode = slicer.util.getNode("ScalePoints" + NodeOrder[i][-3:])
  ScalePointsNode.AddFiducial(float(Rs), float(As), float(Ss))
  ScalePointsNode.SetNthFiducialLabel(ScalePointsNode.GetNumberOfFiducials(), CorrespondingLandmarksNode.GetNthFiducialLabel(i)[:-1] + 'S')
  ScalePointsNode.AddFiducial(float(Ri), float(Ai), float(Si))
  ScalePointsNode.SetNthFiducialLabel(ScalePointsNode.GetNumberOfFiducials(), CorrespondingLandmarksNode.GetNthFiducialLabel(i+1)[:-1] + 'I')
