NoiseStartStopInc = [2, 6, 1]
MarkupNodes = slicer.util.getNodesByClass('vtkMRMLMarkupsFiducialNode')
Widget = slicer.modules.modeltopatientregistration.widgetRepresentation()
InputPanel = Widget.children()[2]
FromInputSelector = InputPanel.children()[2]
FromInputSelector.setCurrentNode(slicer.util.getNode('UsLandmarks_Atlas'))
ToInputSelector = InputPanel.children()[4]
FromOutputSelector = InputPanel.children()[6]
ToOutputSelector = InputPanel.children()[8]
GeneratePoints = InputPanel.children()[-2]
InputPanel.children()[-4].checked = (True)
InputPanel.children()[-3].checked = (True)

#for StdDev in range(NoiseStartStopInc[0], NoiseStartStopInc[1], NoiseStartStopInc[2]):
for FiducialNode in MarkupNodes:
  if FiducialNode.GetName() != 'UsLandmarks_Atlas':
    ToInputSelector.setCurrentNode(FiducialNode)
    FromOutputNode = slicer.vtkMRMLMarkupsFiducialNode()
    FromOutputNode.SetName('Model' + FiducialNode.GetName()[12:15] + 'Points') # + str(StdDev) + 'mmStdDev')
    slicer.mrmlScene.AddNode(FromOutputNode)
    FromOutputSelector.setCurrentNode(FromOutputNode)
    ToOutputNode = slicer.vtkMRMLMarkupsFiducialNode()
    ToOutputNode.SetName('Patient' + FiducialNode.GetName()[12:15] + 'Points') # + str(StdDev) + 'mmStdDev')
    slicer.mrmlScene.AddNode(ToOutputNode)
    ToOutputSelector.setCurrentNode(ToOutputNode)
    GeneratePoints.click()