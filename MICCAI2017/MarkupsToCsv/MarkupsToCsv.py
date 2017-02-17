import csv
OutputDir = 'C:\Users\church\Documents\Winter2017\MICCAI2017\Data'
<<<<<<< HEAD
OutputFile = '\DeepLearningData028.csv'
=======
OutputFile = '\DeepLearningData.csv'
>>>>>>> bb0dbf51e9e6252772509f111b751df3a2e3a0ad
TrP = []    # Transverse process landmarks
SP = []     # Scale points
Nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')

for MarkupsNode in Nodes:
  if MarkupsNode.GetName()[0] == 'T':
    TrP.append(MarkupsNode)
  else:
    SP.append(MarkupsNode)

TrP.sort(key=lambda MarkupsNode: MarkupsNode.GetName())
SP.sort(key=lambda MarkupsNode: MarkupsNode.GetName())

with open(OutputDir + OutputFile, 'wb') as Output:
  OutputWriter = csv.writer(Output)
  OutputWriter.writerow(['SupLeftR', 'SupLeftA', 'SupLeftS', 'SupRightR', 'SupRightA', 'SupRightS', 'LeftR', 'LeftA', 'LeftS', 'RightR', 'RightA', 'RightS',\
    'InfLeftR', 'InfLeftA', 'InfLeftS', 'InfRightR', 'InfRightA', 'InfRightS', 'SupAntR', 'SupAntA', 'SupAntS', 'InfAntR', 'InfAntA', 'InfAntS'])
  for (LandmarkNode, ScaleNode) in zip(TrP, SP):
    if LandmarkNode.GetName()[-3:] != ScaleNode.GetName()[-3:]:
      print "Error - " + LandmarkNode.GetName() + " does not correspond to " + ScaleNode.GetName()
      print "   check input set correspondence"
      break
    for NonBoundaryVertebra in range(1, (ScaleNode.GetNumberOfFiducials()/2) - 2):    # This should exclude trying to captur boundary vertebrae in triplets, as they have only one neighbor
      AvgPos = [0, 0, 0]    # To be subtracted from all coords, centering the input vector
      SupLeftPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) - 2, 0)
      SupRightPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) - 1, 0)
      LeftPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2), 0)
      RightPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) + 1, 0)
      InfLeftPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) + 2, 0)
      InfRightPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) + 3, 0)
      SupAntPoint = ScaleNode.GetMarkupPointVector((NonBoundaryVertebra * 2), 0)
      InfAntPoint = ScaleNode.GetMarkupPointVector((NonBoundaryVertebra * 2) + 1, 0)
      
      #AvgPos[0] = (SupLeftPoint[0] + SupRightPoint[0] + LeftPoint[0] + RightPoint[0] + InfLeftPoint[0] + InfRightPoint[0] + SupAntPoint[0] + InfAntPoint[0]) / 8
      #AvgPos[1] = (SupLeftPoint[1] + SupRightPoint[1] + LeftPoint[1] + RightPoint[1] + InfLeftPoint[1] + InfRightPoint[1] + SupAntPoint[1] + InfAntPoint[1]) / 8
      #AvgPos[2] = (SupLeftPoint[2] + SupRightPoint[2] + LeftPoint[2] + RightPoint[2] + InfLeftPoint[2] + InfRightPoint[2] + SupAntPoint[2] + InfAntPoint[2]) / 8
      MaxAbsPos = 1
      #MaxAbsPos = max(abs(SupLeftPoint[0]), abs(SupLeftPoint[1]), abs(SupLeftPoint[2]), abs(SupRightPoint[0]), abs(SupRightPoint[1]), abs(SupRightPoint[2]), \
      #  abs(LeftPoint[0]), abs(LeftPoint[1]), abs(LeftPoint[2]), abs(RightPoint[0]), abs(RightPoint[1]), abs(RightPoint[2]), \
      #  abs(InfLeftPoint[0]), abs(InfLeftPoint[1]), abs(InfLeftPoint[2]), abs(InfRightPoint[0]), abs(InfRightPoint[1]), abs(InfRightPoint[2]), \
      #  abs(SupAntPoint[0]), abs(SupAntPoint[1]), abs(SupAntPoint[2]), abs(InfAntPoint[0]), abs(InfAntPoint[1]), abs(InfAntPoint[2]))         # To divide point coordinates for normalization
        
      OutputWriter.writerow([(SupLeftPoint[0] - AvgPos[0])/MaxAbsPos, (SupLeftPoint[1] - AvgPos[1])/MaxAbsPos, (SupLeftPoint[2] - AvgPos[2])/MaxAbsPos, (SupRightPoint[0] - AvgPos[0])/MaxAbsPos, (SupRightPoint[1] - AvgPos[1])/MaxAbsPos, (SupRightPoint[2] - AvgPos[2])/MaxAbsPos, \
        (LeftPoint[0] - AvgPos[0])/MaxAbsPos, (LeftPoint[1] - AvgPos[1])/MaxAbsPos, (LeftPoint[2] - AvgPos[2])/MaxAbsPos, (RightPoint[0] - AvgPos[0])/MaxAbsPos, (RightPoint[1] - AvgPos[1])/MaxAbsPos, (RightPoint[2] - AvgPos[2])/MaxAbsPos, \
        (InfLeftPoint[0] - AvgPos[0])/MaxAbsPos, (InfLeftPoint[1] - AvgPos[1])/MaxAbsPos, (InfLeftPoint[2] - AvgPos[2])/MaxAbsPos, (InfRightPoint[0] - AvgPos[0])/MaxAbsPos, (InfRightPoint[1] - AvgPos[1])/MaxAbsPos, (InfRightPoint[2] - AvgPos[2])/MaxAbsPos, \
        (SupAntPoint[0] - AvgPos[0])/MaxAbsPos, (SupAntPoint[1] - AvgPos[1])/MaxAbsPos, (SupAntPoint[2]  - AvgPos[2])/MaxAbsPos, (InfAntPoint[0] - AvgPos[0])/MaxAbsPos, (InfAntPoint[1] - AvgPos[1])/MaxAbsPos, (InfAntPoint[2] - AvgPos[2])/MaxAbsPos])
