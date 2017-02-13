import vtkSegmentationCorePython as Seg
Widget = slicer.modules.segmentations.widgetRepresentation()
SegmentSelector = Widget.children()[2]
ImportPanel = Widget.children()[-1]
ImportModelComboBox = ImportPanel.children()[1]
ImportButton = ImportPanel.children()[3]
AllModels = slicer.util.getNodesByClass('vtkMRMLModelNode')
PatientModels = []
Registrations = []

if slicer.util.getNode("Patients"):
  slicer.mrmlScene.RemoveNode(slicer.util.getNode("Patients"))

if slicer.util.getNode('Registrations'):
  slicer.mrmlScene.RemoveNode(slicer.util.getNode('Registrations'))

for Model in AllModels:
  if Model.GetName()[0] == "M":   # "M" for MergedAtlas###
    Registrations.append(Model)
    #print "Model " + Model.GetName() + " added to Registrations"
    continue
  if len(Model.GetName()) == 3:   # Ground truth name format is: ###
    #print "Model " + Model.GetName() + " added to PatientModels"
    PatientModels.append(Model)

Registrations.sort(key=lambda Model: Model.GetName())
PatientModels.sort(key=lambda Model: Model.GetName())

PatientSegments = slicer.vtkMRMLSegmentationNode()
PatientSegments.SetName('Patients')

for PatientModel in PatientModels:
  CurrentSegment = Seg.vtkSegment()
  CurrentSegment.SetName(PatientModel.GetName())
  ModelToSegTransform = vtk.vtkGeneralTransform()
  slicer.vtkMRMLTransformNode().GetTransformBetweenNodes(PatientModel.GetParentTransformNode(), PatientSegments.GetParentTransformNode(), ModelToSegTransform)
  transformFilter = vtk.vtkTransformPolyDataFilter()
  transformFilter.SetInputData(PatientModel.GetPolyData())
  transformFilter.SetTransform(ModelToSegTransform)
  transformFilter.Update()
  PolyData = vtk.vtkPolyData()
  PolyData.DeepCopy(PatientModel.GetPolyData())
  CurrentSegment.AddRepresentation(Seg.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName(), PolyData)
  LabelmapRepresentation = CurrentSegment.GetRepresentation(Seg.vtkSegmentationConverter.GetSegmentationBinaryLabelmapRepresentationName())
  PatientSegments.GetSegmentation().AddSegment(CurrentSegment)

PatientSegments.GetSegmentation().SetMasterRepresentationName(Seg.vtkSegmentationConverter.GetSegmentationBinaryLabelmapRepresentationName())
slicer.mrmlScene.AddNode(PatientSegments)
SegmentSelector.setCurrentNode(PatientSegments)

RegistrationSegments = slicer.vtkMRMLSegmentationNode()
RegistrationSegments.SetName('Registrations')

for RegistrationModel in Registrations:
  CurrentSegment = Seg.vtkSegment()
  CurrentSegment.SetName(RegistrationModel.GetName())
  ModelToSegTransform = vtk.vtkGeneralTransform()
  slicer.vtkMRMLTransformNode().GetTransformBetweenNodes(RegistrationModel.GetParentTransformNode(), RegistrationSegments.GetParentTransformNode(), ModelToSegTransform)
  transformFilter = vtk.vtkTransformPolyDataFilter()
  transformFilter.SetInputData(RegistrationModel.GetPolyData())
  transformFilter.SetTransform(ModelToSegTransform)
  transformFilter.Update()
  PolyData = vtk.vtkPolyData()
  PolyData.DeepCopy(RegistrationModel.GetPolyData())
  CurrentSegment.AddRepresentation(Seg.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName(), PolyData)
  LabelmapRepresentation = CurrentSegment.GetRepresentation(Seg.vtkSegmentationConverter.GetSegmentationBinaryLabelmapRepresentationName())
  RegistrationSegments.GetSegmentation().AddSegment(CurrentSegment)

RegistrationSegments.GetSegmentation().SetMasterRepresentationName(Seg.vtkSegmentationConverter.GetSegmentationBinaryLabelmapRepresentationName())
slicer.mrmlScene.AddNode(RegistrationSegments)
SegmentSelector.setCurrentNode(RegistrationSegments)
