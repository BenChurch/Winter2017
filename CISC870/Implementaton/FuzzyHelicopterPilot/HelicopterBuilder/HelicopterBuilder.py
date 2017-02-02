import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# Helicopter class
#
class Helicopter(Name):
  def __init__(self):
    print "Helicopter " + Name + " initialized"
    
  def Build(self, FuselageMass, FuselageRadius, TailBoomMass, TailBoomLength, TailBoomRadius, RotorCylinderMass, RotorCylinderLength, RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorMass, MainRotorRadius, TailRotorMass, TailRotorRadius):
    self.CreateGeomtricModel(FuselageRadius,  TailBoomLength, TailBoomRadius, RotorCylinderLength, RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorRadius, TailRotorRadius)

  def CreateGeomtricModel(FuselageRadius,  TailBoomLength, TailBoomRadius, RotorCylinderLength, RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorRadius, TailRotorRadius):
    CreateModelsLogic = slicer.modules.createmodels.logic()
    
    # Fuselage
    self.FuselageGeometricModel = CreateModelsLogic.CreateSphere(FuselageRadius)
    self.FuselageGeometricModel.SetName("Fuselage")
    self.FuselageAxes = CreateModelsLogic.CreateCoordinate(FuselageRadius * 2, FuselageRadius / 5)

    # Tail boom
    self.TailBoomGeometricModel = CreateModelsLogic.CreateCylinder(TailBoomLength, TailBoomRadius)
    FuselageToBoomAssemblyTransform = vtk.vtkMatrix4x4()
    FuselageToBoomAssemblyTransform.SetElement(0, 3, -1 * (FuselageRadius + TailBoomLength / 2))
    FuselageToBoomAssemblyTransform.SetElement(0, 2, -1)
    FuselageToBoomAssemblyTransform.SetElement(2, 0, 1)
    BoomToFuselageNode = slicer.vtkMRMLTransformNode()
    BoomToFuselageNode.SetAndObserveMatrixTransformToParent(FuselageToBoomAssemblyTransform)
    
    # Rotor cylinder
    self.RotorCylinderGeometricModel = CreateModelsLogic.CreateCylinder(RotorCylinderLength, RotorCylinderOuterRadius)
    BoomToCylinderAssemblyTransform = vtk.vtkMatrix4x4()
    BoomToCylinderAssemblyTransform.SetElement(1,2,1)
    BoomToCylinderAssemblyTransform.SetElement(2,1,-1)
    BoomToCylinderAssemblyTransform.SetElement(2,3,-1 * (FuselageRadius + TailBoomLength + RotorCylinderOuterRadius/2))
#
# HelicopterBuilder
#

class HelicopterBuilder(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Helicopter Builder" 
    self.parent.categories = ["Fuzzy Logic"]
    self.parent.dependencies = []
    self.parent.contributors = ["Ben Church (Queen's University)"] 
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    self.parent.acknowledgementText = """

""" # replace with organization, grant and thanks.

#
# HelicopterBuilderWidget
#

class HelicopterBuilderWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    AttributesCollapsibleButton = ctk.ctkCollapsibleButton()
    AttributesCollapsibleButton.text = "Component attributes"
    self.layout.addWidget(AttributesCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(AttributesCollapsibleButton)

    
    #
    # Fuselage properties
    #
    self.FuselageMassSlider = ctk.ctkSliderWidget()
    self.FuselageMassSlider.singleStep = 1
    self.FuselageMassSlider.minimum = 1000
    self.FuselageMassSlider.maximum = 5000
    self.FuselageMassSlider.value = 2000
    self.FuselageMassSlider.setToolTip("Set fuselage mass.")
    parametersFormLayout.addRow("Fuselage Mass", self.FuselageMassSlider)

    self.FuselageRadiusSlider = ctk.ctkSliderWidget()
    self.FuselageRadiusSlider.singleStep = 0.1
    self.FuselageRadiusSlider.minimum = 0.5
    self.FuselageRadiusSlider.maximum = 2
    self.FuselageRadiusSlider.value = 1
    self.FuselageRadiusSlider.setToolTip("Set fuselage radius.")
    parametersFormLayout.addRow("Fuselage Radius", self.FuselageRadiusSlider)
    
    #
    # Tail boom properties
    #
    self.TailMassSlider = ctk.ctkSliderWidget()
    self.TailMassSlider.singleStep = 1
    self.TailMassSlider.minimum = 500
    self.TailMassSlider.maximum = 4000
    self.TailMassSlider.value = 1000
    self.TailMassSlider.setToolTip("Set tail boom mass.")
    parametersFormLayout.addRow("Tail Boom Mass", self.TailMassSlider)
    
    self.TailRadiusSlider = ctk.ctkSliderWidget()
    self.TailRadiusSlider.singleStep = 0.05
    self.TailRadiusSlider.minimum = 0.1
    self.TailRadiusSlider.maximum = 1
    self.TailRadiusSlider.value = 0.5
    self.TailRadiusSlider.setToolTip("Set tail boom radius.")
    parametersFormLayout.addRow("Tail Boom Radius", self.TailRadiusSlider)
    
    self.TailLengthSlider = ctk.ctkSliderWidget()
    self.TailLengthSlider.singleStep = 0.05
    self.TailLengthSlider.minimum = 0.5
    self.TailLengthSlider.maximum = 5
    self.TailLengthSlider.value = 1
    self.TailLengthSlider.setToolTip("Set tail boom length.")
    parametersFormLayout.addRow("Tail Boom Length", self.TailLengthSlider)
    
    #
    # Rotor cylinder properties
    #
    self.RotorCylinderMassSlider = ctk.ctkSliderWidget()
    self.RotorCylinderMassSlider.singleStep = 1
    self.RotorCylinderMassSlider.minimum = 10
    self.RotorCylinderMassSlider.maximum = 500
    self.RotorCylinderMassSlider.value = 50
    self.RotorCylinderMassSlider.setToolTip("Set rotor cylinder mass.")
    parametersFormLayout.addRow("Rotor Cylinder Mass", self.RotorCylinderMassSlider)
    
    self.RotorCylinderLengthSlider = ctk.ctkSliderWidget()
    self.RotorCylinderLengthSlider.singleStep = 0.05
    self.RotorCylinderLengthSlider.minimum = 0.1
    self.RotorCylinderLengthSlider.maximum = 1
    self.RotorCylinderLengthSlider.value = 0.5
    self.RotorCylinderLengthSlider.setToolTip("Set rotor cylinder length.")
    parametersFormLayout.addRow("Rotor Cylinder Length", self.RotorCylinderLengthSlider)
    
    self.RotorCylinderInnerRadiusSlider = ctk.ctkSliderWidget()
    self.RotorCylinderInnerRadiusSlider.singleStep = 0.01
    self.RotorCylinderInnerRadiusSlider.minimum = 0.05
    self.RotorCylinderInnerRadiusSlider.maximum = 1
    self.RotorCylinderInnerRadiusSlider.value = 0.1
    self.RotorCylinderInnerRadiusSlider.setToolTip("Set rotor inner radius (must be larger than tail fan radius).")
    parametersFormLayout.addRow("Rotor Cylinder Inner Radius", self.RotorCylinderInnerRadiusSlider)

    self.RotorCylinderOuterRadiusSlider = ctk.ctkSliderWidget()
    self.RotorCylinderOuterRadiusSlider.singleStep = 0.01
    self.RotorCylinderOuterRadiusSlider.minimum = 0.3
    self.RotorCylinderOuterRadiusSlider.maximum = 1.5
    self.RotorCylinderOuterRadiusSlider.value = self.RotorCylinderInnerRadiusSlider.value
    self.RotorCylinderOuterRadiusSlider.setToolTip("Set rotor outer radius (must be larger than inner radius).")
    parametersFormLayout.addRow("Rotor Cylinder Outer Radius", self.RotorCylinderOuterRadiusSlider)
    
    #
    # Main rotor properties
    #
    self.MainRotorMassSlider = ctk.ctkSliderWidget()
    self.MainRotorMassSlider.singleStep = 1
    self.MainRotorMassSlider.minimum = 10
    self.MainRotorMassSlider.maximum = 250
    self.MainRotorMassSlider.value = 50
    self.MainRotorMassSlider.setToolTip("Set main rotor mass.")
    parametersFormLayout.addRow("Main Rotor Mass", self.MainRotorMassSlider)
    
    self.MainRotorRadiusSlider = ctk.ctkSliderWidget()
    self.MainRotorRadiusSlider.singleStep = 0.1
    self.MainRotorRadiusSlider.minimum = 1
    self.MainRotorRadiusSlider.maximum = 5
    self.MainRotorRadiusSlider.value = 2
    self.MainRotorRadiusSlider.setToolTip("Set main rotor radius.")
    parametersFormLayout.addRow("Main Rotor Radius", self.MainRotorRadiusSlider)
    
    #
    # Tail rotor properties
    #
    
    self.TailRotorMassSlider = ctk.ctkSliderWidget()
    self.TailRotorMassSlider.singleStep = 0.01
    self.TailRotorMassSlider.minimum = 1
    self.TailRotorMassSlider.maximum = 50
    self.TailRotorMassSlider.value = 10
    self.TailRotorMassSlider.setToolTip("Set tail rotor mass.")
    parametersFormLayout.addRow("Tail Rotor Mass", self.TailRotorMassSlider)

    self.TailRotorRadiusSlider = ctk.ctkSliderWidget()
    self.TailRotorRadiusSlider.singleStep = 0.01
    self.TailRotorRadiusSlider.minimum = 0.1
    self.TailRotorRadiusSlider.maximum = 1
    self.TailRotorRadiusSlider.value = self.RotorCylinderInnerRadiusSlider.value
    self.TailRotorRadiusSlider.setToolTip("Set tail rotor radius (must be smaller than RotorCylinder inner radius).")
    parametersFormLayout.addRow("Tail Rotor Radius", self.TailRotorRadiusSlider)
    
    #
    # Check box to create individual component center-of-mass coordinate axes models
    #
    self.CreateComponentAxesCheckBox = qt.QCheckBox()
    self.CreateComponentAxesCheckBox.checked = 0
    self.CreateComponentAxesCheckBox.setToolTip("If checked, models of each helicopter component's center of mass coordiante axes will be produced")
    parametersFormLayout.addRow("Create componenet axes", self.CreateComponentAxesCheckBox)
    
    #
    # Check box to create helicopter center-of-mass coordinate axes model
    #
    self.CreateHelicopterAxesCheckBox = qt.QCheckBox()
    self.CreateHelicopterAxesCheckBox.checked = 0
    self.CreateHelicopterAxesCheckBox.setToolTip("If checked, models the helicopter's center of mass coordiante axes will be produced")
    parametersFormLayout.addRow("Create helicopter axes", self.CreateHelicopterAxesCheckBox)

    #
    # Build Button
    #
    self.BuildButton = qt.QPushButton("Build")
    self.BuildButton.toolTip = "Build the model."
    self.BuildButton.enabled = True
    parametersFormLayout.addRow(self.BuildButton)

    # connections
    self.BuildButton.connect('clicked(bool)', self.onBuildButton)


    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    #self.onSelect()

  def cleanup(self):
    pass

  #def onSelect(self):
    #self.BuildButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onBuildButton(self):
    Logic = HelicopterBuilderLogic()
    FuselageMass = self.FuselageMassSlider.value
    FuselageRadius = self.FuselageRadiusSlider.value
    TailBoomMass = self.TailMassSlider.value
    TailBoomLength = self.TailLengthSlider.value
    TailBoomRadius = self.TailRadiusSlider.value
    RotorCylinderMass = self.RotorCylinderMassSlider.value
    RotorCylinderLength = self.RotorCylinderLengthSlider.value
    RotorCylinderInnerRadius = self.RotorCylinderInnerRadiusSlider.value
    RotorCylinderOuterRadius = self.RotorCylinderOuterRadiusSlider.value
    MainRotorMass = self.MainRotorMassSlider.value
    MainRotorRadius = self.MainRotorRadiusSlider.value
    TailRotorMass = self.TailRotorMassSlider.value
    TailRotorRadius = self.TailRotorRadiusSlider.value
    if not Logic.CheckIfAttributesValid(RotorCylinderInnerRadius, RotorCylinderOuterRadius, TailRotorRadius):
      return
    Logic.BuildModel(FuselageMass, FuselageRadius, TailBoomMass, TailBoomLength, TailBoomRadius, RotorCylinderMass, RotorCylinderLength, \
      RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorMass, MainRotorRadius, TailRotorMass, TailRotorRadius)

#
# HelicopterBuilderLogic
#

class HelicopterBuilderLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


  def CheckIfAttributesValid(self, RotorCylinderInnerRadius, RotorCylinderOuterRadius, TailRotorRadius):
    """
    Validates if the helicopter geometry is allowed (tail rotor components don't intersect)
    """
    if RotorCylinderInnerRadius > RotorCylinderOuterRadius:
      print "Error - RotorCylinderInnerRadius larger than RotorCylinderOuterRadius"
      print "   Adjust component attributes accordingly"
      return False
    if TailRotorRadius > RotorCylinderInnerRadius:
      print "Error - TailRotorRadius larger than RotorCylinderInnerRadius"
      print "Adjust component attributes accordingly"
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def BuildModel(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Build helicopter model
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('HelicopterBuilderTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class HelicopterBuilderTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_HelicopterBuilder1()

  def test_HelicopterBuilder1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = HelicopterBuilderLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
