# Make sure to go into IGT's Fiducial Registration Wizard and set update to manual

AllLandmarkSets = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')
ModelSets = []
PatientSets = []
Transforms = []
Widget = slicer.modules.fiducialregistrationwizard.widgetRepresentation()
InputForm = Widget.children()[3]
FromCollapsible = InputForm.children()[3]
FromComboBox = FromCollapsible.children()[1]
ToCollapsible = InputForm.children()[4]
ToComboBox = ToCollapsible.children()[1]
ParametersForm = InputForm.children()[-2]

ParametersForm.children()[6].click()  # Set to warping transform
# Does not current change from Auto-update to manual, do this manaully for now
for LandmarkSet in AllLandmarkSets:
  if LandmarkSet.GetName()[0] == "P":
    PatientSets.append(LandmarkSet)
  else:
    ModelSets.append(LandmarkSet)

PatientSets.sort(key=lambda LandmarkNode: LandmarkNode.GetName())
ModelSets.sort(key=lambda LandmarkNode: LandmarkNode.GetName())

for (ModelSet, PatientSet) in zip(ModelSets, PatientSets):
  FromComboBox.setCurrentNode(slicer.util.getNode(ModelSet.GetName()))
  ToComboBox.setCurrentNode(slicer.util.getNode(PatientSet.GetName()))
  Transform = slicer.vtkMRMLTransformNode()
  #Transform = vtk.vtkThinPlateSplineTransform()
  Transform.SetName('ModelToPatient' + ModelSet.GetName()[5:8])
  slicer.mrmlScene.AddNode(Transform)
  ParametersForm.children()[1].setCurrentNode(Transform)
  ParametersForm.children()[-2].click() 
  Transforms.append(Transform)
  print ModelSet.GetName() + "  - " + PatientSet.GetName()
  
# ASSERT all thin-plate spline transforms are populated

# Now apply and harden all transforms
for Transform in Transforms:
  CurrentModel = slicer.util.getNode('MergedAtlas' + Transform.GetName()[-3:])
  CurrentModel.SetAndObserveTransformNodeID(Transform.GetID())
  CurrentModel.HardenTransform()
