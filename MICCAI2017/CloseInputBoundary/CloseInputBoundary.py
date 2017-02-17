# Extrapolates patient spine one vertebra above and below so all vertebrae have 6 3D input points for DeepLearning scale estimation
Labels = ['X','T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12','L1','L2','L3','L4','L5','Y']
Nodes = slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode')
for N in Nodes:
  NewTopVertebra = Labels[Labels.index(N.GetNthFiducialLabel(0)[:2]) - 1]
  NewBottomVertebra = Labels[Labels.index(N.GetNthFiducialLabel(N.GetNumberOfFiducials()-1)[:2]) + 1]
  TopLeftPoint = N.GetMarkupPointVector(0, 0)
  TopRightPoint = N.GetMarkupPointVector(1, 0)
  BottomLeftPoint = N.GetMarkupPointVector(N.GetNumberOfFiducials() - 2, 0)
  BottomRightPoint = N.GetMarkupPointVector(N.GetNumberOfFiducials() - 1, 0)
  BelowTopLeft = N.GetMarkupPointVector(2, 0)
  BelowTopRight = N.GetMarkupPointVector(3, 0)
  AboveBottomLeft = N.GetMarkupPointVector(N.GetNumberOfFiducials() - 4, 0)
  AboveBottomRight = N.GetMarkupPointVector(N.GetNumberOfFiducials() - 3, 0)
  UpVector = [0, 0, 0]
  DownVector = [0, 0, 0]
  for dim in range (3):
    UpVector[dim] = ((TopLeftPoint[dim] - BelowTopLeft[dim]) + (TopRightPoint[dim] - BelowTopRight[dim])) / 2.0
    DownVector[dim] = ((BottomLeftPoint[dim] - AboveBottomLeft[dim]) + (BottomRightPoint[dim] - AboveBottomRight[dim])) / 2.0 
  NewNode = slicer.vtkMRMLMarkupsFiducialNode()
  NewNode.SetName(N.GetName() + 'Closed')
  NewNode.AddFiducial(TopLeftPoint[0] + UpVector[0], TopLeftPoint[1] + UpVector[1], TopLeftPoint[2] + UpVector[2])
  NewNode.SetNthFiducialLabel(0, NewTopVertebra + 'L')
  NewNode.AddFiducial(TopRightPoint[0] + UpVector[0], TopRightPoint[1] + UpVector[1], TopRightPoint[2] + UpVector[2])
  NewNode.SetNthFiducialLabel(1, NewTopVertebra + 'R')
  for i in range(N.GetNumberOfFiducials()):
    Point = N.GetMarkupPointVector(i, 0)
    NewPoint = [0, 0, 0]
    for dim in range(3):
      NewPoint[dim] = Point[dim]
    NewNode.AddFiducialFromArray(NewPoint)
    NewNode.SetNthFiducialLabel(NewNode.GetNumberOfFiducials()-1, N.GetNthFiducialLabel(i))
  NewNode.AddFiducial(BottomLeftPoint[0] + DownVector[0], BottomLeftPoint[1] + DownVector[1], BottomLeftPoint[2] + DownVector[2])
  NewNode.SetNthFiducialLabel(NewNode.GetNumberOfFiducials()-1, NewBottomVertebra + 'L')
  NewNode.AddFiducial(BottomRightPoint[0] + DownVector[0], BottomRightPoint[1] + DownVector[1], BottomRightPoint[2] + DownVector[2])
  NewNode.SetNthFiducialLabel(NewNode.GetNumberOfFiducials()-1, NewBottomVertebra + 'R')
  slicer.mrmlScene.RemoveNode(N)
  slicer.mrmlScene.AddNode(NewNode)