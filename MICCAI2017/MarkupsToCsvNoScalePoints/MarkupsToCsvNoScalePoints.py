import csv
#OutputDir = 'C:\Users\church\Documents\Winter2017\MICCAI2017\Data'
OutputDir = 'C:\Users\Ben\Documents\Masters16_17\Winter2017\MICCAI2017\Data'
OutputFile = '\PredictAllVertebrae007'
Nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')

#with open(OutputDir + OutputFile + Nodes.GetItemAsObject(i).GetName()[-9:-6] + '.csv', 'wb') as Output:
with open(OutputDir + OutputFile + '.csv', 'wb') as Output:
  OutputWriter = csv.writer(Output)
  OutputWriter.writerow(['SupLeftR', 'SupLeftA', 'SupLeftS', 'SupRightR', 'SupRightA', 'SupRightS', 'LeftR', 'LeftA', 'LeftS', 'RightR', 'RightA', 'RightS',\
  'InfLeftR', 'InfLeftA', 'InfLeftS', 'InfRightR', 'InfRightA', 'InfRightS'])
  for i, LandmarkNode in enumerate(Nodes):
    for NonBoundaryVertebra in range(1, (LandmarkNode.GetNumberOfFiducials()/2)-1):    # This should exclude trying to captur boundary vertebrae in triplets, as they have only one neighbor
      AvgPos = [0, 0, 0]    # To be subtracted from all coords, centering the input vector
      SupLeftPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) - 2, 0)
      SupRightPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) - 1, 0)
      LeftPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2), 0)
      RightPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) + 1, 0)
      InfLeftPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) + 2, 0)
      InfRightPoint = LandmarkNode.GetMarkupPointVector((NonBoundaryVertebra * 2) + 3, 0)
      #AvgPos[0] = (SupLeftPoint[0] + SupRightPoint[0] + LeftPoint[0] + RightPoint[0] + InfLeftPoint[0] + InfRightPoint[0]) / 6
      #AvgPos[1] = (SupLeftPoint[1] + SupRightPoint[1] + LeftPoint[1] + RightPoint[1] + InfLeftPoint[1] + InfRightPoint[1]) / 6
      #AvgPos[2] = (SupLeftPoint[2] + SupRightPoint[2] + LeftPoint[2] + RightPoint[2] + InfLeftPoint[2] + InfRightPoint[2]) / 6
      MaxAbsPos = 1
      #MaxAbsPos = max(abs(SupLeftPoint[0]), abs(SupLeftPoint[1]), abs(SupLeftPoint[2]), abs(SupRightPoint[0]), abs(SupRightPoint[1]), abs(SupRightPoint[2]), \
      #  abs(LeftPoint[0]), abs(LeftPoint[1]), abs(LeftPoint[2]), abs(RightPoint[0]), abs(RightPoint[1]), abs(RightPoint[2]), \
      #  abs(InfLeftPoint[0]), abs(InfLeftPoint[1]), abs(InfLeftPoint[2]), abs(InfRightPoint[0]), abs(InfRightPoint[1]), abs(InfRightPoint[2]))
      OutputWriter.writerow([(SupLeftPoint[0] - AvgPos[0])/MaxAbsPos, (SupLeftPoint[1] - AvgPos[1])/MaxAbsPos, (SupLeftPoint[2] - AvgPos[2])/MaxAbsPos, (SupRightPoint[0] - AvgPos[0])/MaxAbsPos, (SupRightPoint[1] - AvgPos[1])/MaxAbsPos, (SupRightPoint[2] - AvgPos[2])/MaxAbsPos, \
        (LeftPoint[0] - AvgPos[0])/MaxAbsPos, (LeftPoint[1] - AvgPos[1])/MaxAbsPos, (LeftPoint[2] - AvgPos[2])/MaxAbsPos, (RightPoint[0] - AvgPos[0])/MaxAbsPos, (RightPoint[1] - AvgPos[1])/MaxAbsPos, (RightPoint[2] - AvgPos[2])/MaxAbsPos, \
        (InfLeftPoint[0] - AvgPos[0])/MaxAbsPos, (InfLeftPoint[1] - AvgPos[1])/MaxAbsPos, (InfLeftPoint[2] - AvgPos[2])/MaxAbsPos, (InfRightPoint[0] - AvgPos[0])/MaxAbsPos, (InfRightPoint[1] - AvgPos[1])/MaxAbsPos, (InfRightPoint[2] - AvgPos[2])/MaxAbsPos,  LandmarkNode.GetName()])
        