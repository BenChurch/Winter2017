Nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')
TrP = []
SP = []
for Node in Nodes:
  if Node.GetName()[0] == 'T':
    TrP.append(Node)
  else: SP.append(Node)

TrP.sort(key=lambda MarkupsNode: MarkupsNode.GetName())
SP.sort(key=lambda MarkupsNode: MarkupsNode.GetName())

for (TrPNode, SPNode) in zip(TrP, SP):
  for P in range(SPNode.GetNumberOfFiducials()):
    PointV = SPNode.GetMarkupPointVector(P,0)
    Point = [0,0,0]
    for dim in range(3):
      Point[dim] = PointV[dim]
    TrPNode.AddFiducialFromArray(PointV)
    TrPNode.SetNthFiducialLabel(TrPNode.GetNumberOfFiducials(), SPNode.GetNthFiducialLabel(P))