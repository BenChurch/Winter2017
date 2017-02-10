# Automatically names points in most recent MarkupsNode for scaling points

Nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')
LatestNode = Nodes.GetItemAsObject(Nodes.GetNumberOfItems()-1)

FirstVertebra = raw_input('Enter top vertebra name (eg. T4)')
AllowedVertebrae = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12', 'L1', 'L2', 'L3', 'L4', 'L5']

if FirstVertebra in AllowedVertebrae:
  FirstIndex = AllowedVertebrae.index(FirstVertebra)
  for i in range(LatestNode.GetNumberOfFiducials()):
    if i%2 == 0:
      LatestNode.SetNthFiducialLabel(i, AllowedVertebrae[FirstIndex + (i/2)] + 'S')
    else:
      LatestNode.SetNthFiducialLabel(i, AllowedVertebrae[FirstIndex + (i/2)] + 'I')   
else:
  print "Error - Top vertebra name not allowed, doing nothing"
