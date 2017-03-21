import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# Fuzzy library class
#

class FuzzyLogic():
  #def __init__(self)
  import numpy as np
  class UnboundedTrap():
    def __init__(self, LeftJog, RightJog):    # LeftFoot = (x1,y1); RightFoot = (x2,y2)      
      self.LJ = LeftJog
      self.RJ = RightJog
      self.Membership = 0
      # Determine equation of line between feet
      self.slope = (self.RJ[0] - self.LJ[0]) / (self.RJ[1] - self.LJ[1])
    
    def ComputeMembership(self, CrispValue):
      if np.sign(self.slope) < 0:
        if CrispValue > self.RJ[0]: 
          self.Membership = 0
          return
        if CrispValue < self.LJ[0]:
          self.Membership = 0
          return
        else: 
          self.Membership = 1 + (self.slope * (CrispValue - self.LJ[0]))
          return
      else: # if slope is +ve
        if CrispValue > self.RJ[0]:
          self.Membership = 1
          return
        if CrispValue < self.LJ[0]:
          self.Membership = 0
        else:
          self.Membership = 0 + (self.slope * (CrispValue - self.LJ[0]))
          
  class BoundedTrap():      # Should reduce to triangle when LeftShoulder == RightShoulder
    def __init__(self, LeftFoot, LeftShoulder, RightShoulder, RightFoot):
      self.LF = LeftFoot
      self.LS = LeftShoulder
      self.RS = RightShoulder
      self.RF = RightFoot
      self.Membership = 0
      self.LeftSlope = (self.LS - self.LF) / (self.LS - self.LF)
      self.RightSlope = (self.RF - self.RS) / (self.RF - self.RS)
      
    def ComputeMembership(self, CrispValue):
      if CrispValue < self.LF or CrispValue > self.RF:
        self.Membership = 0
        return
      if CrispValue > self.LS and CrispValue < self.RS:
        self.Membership = 1
        return
      if CrispValue > self.LS:   # crisp value falls on right slope
        self.Membership = 1 + (self.RightSlope * (CrispValue - self.RS))
        return
      if CrispValue < self.RS:   # crisp value falls on left slope
        self.Membership = self.LeftSlope * (CrispValue - self.LF)
        return
  
#
# Helicopter class
#
class Helicopter():
  def __init__(self, Name):
    import math
    FL = FuzzyLogic()
    print "Helicopter " + Name + " initialized"
    
    # Constants
    self.Gravity = 9.81
    self.Pi = 3.14159
    self.dt = 0.1   # Approximation of time (s) between physics iterations, needed for changing velocity from acceleration
    
    # Mechanical properties
    self.MaxEnginePower = 20000  # Maximum thrust which can be exerted at the MainRotor (kgs)
    self.MaxMainRotorAngVel = 30 # rad/s
    self.MaxTailPower = 1000    # Maximum thrust from tail fan, in either direction (kgs)
    self.MaxTailRotorAngVel = 30 # rad/3
    self.MaxRotorTilt = 15    # Maximum angle the main rotor can be tilted in cyclic steering (deg)
    
    # Controls state
    self.CyclicAlpha = 0            # Current main rotor tilted (deg)
    self.CyclicTheta = 0            # Direction of tilt of main rotor (deg), 0 being forward 
    self.MainThrottle = 0           # Throttle values range from 0 to 1, multiply by max power
    self.TailThrottle = 0           # Negative value causing negative rotation, etc
    
    # Physics properties
    self.COM = [0,0,0] 
    self.I = [0, 0, 0]  # Moment of interia vector, to be computed about COM
    self.Velocity = [0,0,0]
    self.AngularVelocity = [0,0,0]
    self.Forces = [0,0,0] 
    self.Moments = [0,0,0]  # About COM
    
    # Fuzzy rules
    
    # Position error - set to hover about origin - crisp values come from self.OriginToCOMNode
    LeftErrorLarge = FL.UnboundedTrap((-10,1), (-5,0))
    LeftErrorMed = FL.BoundedTrap(-10,-5,-5,0)
    LeftErrorSmall = FL.UnboundedTrap((-5,0),(0,1))
    RightErrorLarge = FL.UnboundedTrap((5,0), (10,1))
    RightErrorMed = FL.BoundedTrap(0,5,5,10)
    RightErrorSmall = FL.UnboundedTrap((0,0),(5,1))
    
    DownErrorLarge = FL.UnboundedTrap((-10,1), (-5,0))
    DownErrorMed = FL.BoundedTrap(-10,-5,-5,0)
    DownErrorSmall = FL.UnboundedTrap((-5,0),(0,1))
    UpErrorLarge = FL.UnboundedTrap((5,0), (10,1))
    UpErrorMed = FL.BoundedTrap(0,5,5,10)
    UpErrorSmall = FL.UnboundedTrap((0,0),(5,1))

    DownErrorLarge = FL.UnboundedTrap((-10,1), (-5,0))
    DownErrorMed = FL.BoundedTrap(-10,-5,-5,0)
    DownErrorSmall = FL.UnboundedTrap((-5,0),(0,1))
    UpErrorLarge = FL.UnboundedTrap((5,0), (10,1))
    UpErrorMed = FL.BoundedTrap(0,5,5,10)
    UpErrorSmall = FL.UnboundedTrap((0,0),(5,1))
    
    # Rotation errors in rad
    NegRollErrorLarge = FL.UnboundedTrap((-1*(self.Pi/2.0), 1), (-1*(self.Pi/4.0), 0))
    NegRollErrorMed = FL.BoundedTrap(-1*(self.Pi/2.0), -1*(self.Pi/4.0), -1*(self.Pi/4.0), 0)
    NegRollErrorSmall = FL.UnboundedTrap((-1*(self.Pi/4.0), 0), (0,1))
    PosRollErrorLarge = FL.UnboundedTrap((self.Pi/4.0, 0), (self.Pi/2.0, 1))
    PosRollErrorMed = FL.BoundedTrap(0, self.Pi/4.0, self.Pi/4.0, self.Pi/2.0)
    PosRollErrorSmall = FL.UnboundedTrap((0,1), (self.Pi/4.0, 0))
    
    # Angular velocity error - use to keep yaw under control, direction doesn't matter, but don't want to spin fast
    # (rad/s)
    NegSpinErrorLarge = FL.UnboundedTrap((-1*(self.Pi), 1), (-1*(self.Pi/2.0), 0))
    NegSpinErrorMed = FL.BoundedTrap(-1*(self.Pi), -1*(self.Pi/2.0), -1*(self.Pi/2.0), 0)
    NegSpinErrorSmall = FL.UnboundedTrap((-1*(self.Pi/2.0), 0), (0, 1))
    PosSpinErrorLarge = FL.UnboundedTrap((self.Pi/2.0, 0), (self.Pi, 1))
    PosSpinErrorMed = FL.BoundedTrap(0, self.Pi/2.0, self.Pi/2.0, self.Pi)
    PosSpinErrorSmall = FL.UnboundedTrap((self.Pi/2.0, 0), (0, 1))
    
  def Build(self, FuselageMass, FuselageRadius, TailBoomMass, TailBoomLength, TailBoomRadius, RotorCylinderMass, RotorCylinderLength, RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorMass, MainRotorRadius, TailRotorMass, TailRotorRadius, CreateComponentAxesIsChecked, CreateHelicopterAxesIsChecked):
    self.FM = FuselageMass
    self.FR = FuselageRadius
    self.TBM = TailBoomMass
    self.TBL = TailBoomLength
    self.TBR = TailBoomRadius
    self.RCM = RotorCylinderMass
    self.RCL = RotorCylinderLength
    self.RCIR = RotorCylinderInnerRadius
    self.RCOR = RotorCylinderOuterRadius
    self.MRM = MainRotorMass
    self.MRR = MainRotorRadius
    self.TRM = TailRotorMass
    self.TRR = TailRotorRadius
    self.CreateGeomtricModel(CreateComponentAxesIsChecked)
    self.ComputeDynamicsProperties(CreateComponentAxesIsChecked, CreateHelicopterAxesIsChecked)
    
  def CreateGeomtricModel(self, CreateComponentAxesIsChecked=False):
    CreateModelsLogic = slicer.modules.createmodels.logic()
    
    # Fuselage
    self.FuselageGeometricModel = CreateModelsLogic.CreateSphere(self.FR)
    self.FuselageGeometricModel.SetName("Fuselage")
    self.OriginToFuselage = vtk.vtkMatrix4x4()    # Construct fuselage at origin
    self.OriginToFuselageNode = slicer.vtkMRMLTransformNode()
    self.OriginToFuselageNode.SetName('OriginToFuselage')
    self.OriginToFuselageNode.SetAndObserveMatrixTransformToParent(self.OriginToFuselage)
    slicer.mrmlScene.AddNode(self.OriginToFuselageNode)
    
    # All following pieces are constructed relative to center of fuselage. Fuselage will then be transformed relative to Heli center of mass
    self.FuselageToCOMTransform = vtk.vtkMatrix4x4() # Unknown at this point, must instantiate and compute part properties first
    self.FuselageToCOMNode = slicer.vtkMRMLTransformNode()
    # Set as parent once transform matrix is populated

    # Tail boom
    self.TailBoomGeometricModel = CreateModelsLogic.CreateCylinder(self.TBL, self.TBR)
    self.TailBoomGeometricModel.SetName("TailBoom")
    FuselageToBoomAssemblyRotation = vtk.vtkMatrix4x4()
    FuselageToBoomAssemblyRotation.Zero()
    FuselageToBoomAssemblyRotation.SetElement(0, 2, -1)
    FuselageToBoomAssemblyRotation.SetElement(2, 0, 1)
    FuselageToBoomAssemblyRotation.SetElement(1, 1, 1)
    FuselageToBoomAssemblyRotation.SetElement(3, 3, 1)
    self.FuselageToBoomAlignment = slicer.vtkMRMLTransformNode()
    self.FuselageToBoomAlignment.SetAndObserveMatrixTransformToParent(FuselageToBoomAssemblyRotation)
    self.FuselageToBoomAlignment.SetName("FuselageBoomAlignment")
    #slicer.mrmlScene.AddNode(self.FuselageToBoomAlignment)
    self.TailBoomGeometricModel.ApplyTransform(self.FuselageToBoomAlignment.GetTransformToParent())
    self.TailBoomGeometricModel.HardenTransform()
    
    self.FuselageToBoomAssemblyTransform = vtk.vtkMatrix4x4()
    self.FuselageToBoomAssemblyTransform.SetElement(0, 3, -1 * (self.FR + self.TBL / 2))
    self.FuselageBoomAssembly = slicer.vtkMRMLTransformNode()
    self.FuselageBoomAssembly.SetName("FuselageBoomAssembly")
    self.FuselageBoomAssembly.SetAndObserveMatrixTransformToParent(self.FuselageToBoomAssemblyTransform)
    #slicer.mrmlScene.AddNode(self.FuselageBoomAssembly)
    self.TailBoomGeometricModel.ApplyTransform(self.FuselageBoomAssembly.GetTransformToParent())
    self.TailBoomGeometricModel.HardenTransform()
    
    # Origin to Tail Boom
    self.OriginToBoomNode = self.FuselageBoomAssembly    # Identical at the start
    self.OriginToBoomNode.SetName('OriginToBoom')
    slicer.mrmlScene.AddNode(self.OriginToBoomNode)
    
    # Rotor cylinder
    self.RotorCylinderGeometricModel = CreateModelsLogic.CreateCylinder(self.RCL, self.RCOR)
    self.RotorCylinderGeometricModel.SetName('RotorCylinder')
    FuselageToCylinderAssemblyRotation = vtk.vtkMatrix4x4()
    FuselageToCylinderAssemblyRotation.Zero()
    FuselageToCylinderAssemblyRotation.SetElement(0, 0, 1)
    FuselageToCylinderAssemblyRotation.SetElement(1, 2, 1)
    FuselageToCylinderAssemblyRotation.SetElement(2, 1, -1)
    FuselageToCylinderAlignment = slicer.vtkMRMLTransformNode()
    FuselageToCylinderAlignment.SetName('FuselageCylinderAlignment')
    #slicer.mrmlScene.AddNode(FuselageToCylinderAlignment)
    FuselageToCylinderAlignment.SetAndObserveMatrixTransformToParent(FuselageToCylinderAssemblyRotation)
    self.RotorCylinderGeometricModel.ApplyTransform(FuselageToCylinderAlignment.GetTransformToParent())
    self.RotorCylinderGeometricModel.HardenTransform()
    
    FuselageToCylinderAssemblyTransform = vtk.vtkMatrix4x4()
    FuselageToCylinderAssemblyTransform.SetElement(0, 3, -1 * (self.FR + self.TBL + self.RCOR))
    self.FuselageToCylinderNode = slicer.vtkMRMLTransformNode()
    #FuselageToCylinderNode.SetName('FuselageToCylinder')
    self.FuselageToCylinderNode.SetAndObserveMatrixTransformToParent(FuselageToCylinderAssemblyTransform)
    #slicer.mrmlScene.AddNode(FuselageToCylinderNode)
    self.RotorCylinderGeometricModel.ApplyTransform(self.FuselageToCylinderNode.GetTransformToParent())
    self.RotorCylinderGeometricModel.HardenTransform()
    
    # Origin to rotor cylinder
    self.OriginToCylinderNode = self.FuselageToCylinderNode
    self.OriginToCylinderNode.SetName('OriginToCylinder')
    slicer.mrmlScene.AddNode(self.OriginToCylinderNode)
    
    # Main rotor blade
    self.MainRotorGeometricModel = CreateModelsLogic.CreateCylinder(self.FR / 50, self.MRR)
    self.MainRotorGeometricModel.SetName("MainRotor")
    FuselageToMainRotorAssemblyTransform = vtk.vtkMatrix4x4()
    FuselageToMainRotorAssemblyTransform.SetElement(2, 3, self.FR)
    self.FuselageToMainRotorNode = slicer.vtkMRMLTransformNode()
    self.FuselageToMainRotorNode.SetName("FuselageToRotor")
    self.FuselageToMainRotorNode.SetAndObserveMatrixTransformToParent(FuselageToMainRotorAssemblyTransform)
    #slicer.mrmlScene.AddNode(FuselageToMainRotorNode)
    self.MainRotorGeometricModel.ApplyTransform(self.FuselageToMainRotorNode.GetTransformToParent())
    self.MainRotorGeometricModel.HardenTransform()
    
    # Origin to main rotor
    self.OriginToRotorNode = self.FuselageToMainRotorNode
    self.OriginToRotorNode.SetName('OriginToRotor')
    slicer.mrmlScene.AddNode(self.OriginToRotorNode)
    
    # Tail rotor blade
    self.TailRotorGeometricModel = CreateModelsLogic.CreateCylinder(self.FR / 50, self.TRR)
    self.TailRotorGeometricModel.SetName('TailRotor')
    FuselageToTailRotorAlignement = FuselageToCylinderAlignment
    self.TailRotorGeometricModel.ApplyTransform(FuselageToTailRotorAlignement.GetTransformToParent())
    self.TailRotorGeometricModel.HardenTransform()
    self.FuselageToTailNode = slicer.vtkMRMLTransformNode()
    self.FuselageToTailNode.SetAndObserveMatrixTransformToParent(FuselageToCylinderAssemblyTransform)
    self.FuselageToTailNode.SetName('FuselageToTailRotor')
    self.TailRotorGeometricModel.ApplyTransform(self.FuselageToTailNode.GetTransformToParent())
    self.TailRotorGeometricModel.HardenTransform()
    
    # Origin to tail rotor
    self.OriginToTailRotorNode = self.FuselageToTailNode
    self.OriginToTailRotorNode.SetName('OriginToTailRotor')
    slicer.mrmlScene.AddNode(self.OriginToTailRotorNode)
    
    if CreateComponentAxesIsChecked:
      self.FuselageAxes = CreateModelsLogic.CreateCoordinate(self.FR * 2, self.FR / 5)
      self.FuselageAxes.SetName("FuselageAxes")
      
      self.BoomAxes = CreateModelsLogic.CreateCoordinate(self.TBR * 2, self.TBR / 5)
      self.BoomAxes.SetName('BoomAxes')
      self.BoomAxes.ApplyTransform(self.FuselageBoomAssembly.GetTransformToParent())
      self.BoomAxes.HardenTransform()
      
      self.RotorCylinderAxes = CreateModelsLogic.CreateCoordinate(self.RCOR * 2, self.RCOR / 5)
      self.RotorCylinderAxes.SetName('RotorCylinderAxes')
      self.RotorCylinderAxes.ApplyTransform(self.FuselageToCylinderNode.GetTransformToParent())
      self.RotorCylinderAxes.HardenTransform()
    
      self.RotorAxes = CreateModelsLogic.CreateCoordinate(self.MRR, self.MRR/10)
      self.RotorAxes.SetName('RotorAxes')
      self.RotorAxes.ApplyTransform(self.FuselageToMainRotorNode.GetTransformToParent())
      self.RotorAxes.HardenTransform()
    # No need for tail rotor axes, identical to cylinder

  def ComputeDynamicsProperties(self, CreateAxesIsChecked=False, CreateHeliAxesIsCheccked=False):
    #CreateModelsLogic = slicer.modules.createmodels.logic()
    self.TotalMass = self.FM + self.TBM + self.RCM + self.MRM + self.TRM
    
    # Compute center of mass (COM)
    self.COM[0] = ((-1*(self.FR + (self.TBL/2))*self.TBM) - ((self.FR + self.TBL + self.RCOR)*(self.RCM + self.TRM)))/self.TotalMass
    self.COM[2] = (self.FR * self.MRM)/self.TotalMass
    
    IxS1 = (self.FM) * (((2.0/5.0) * (self.FR*self.FR)) + (self.COM[2] ** 2))
    IxS2 = (self.TBM) * ((self.TBR/2.0) + (self.COM[2] ** 2))
    IxS3 = (self.RCM) * ((( 3*(self.RCOR**2 + self.RCIR ** 2) + self.RCL ** 2)/12.0) + (self.COM[2] ** 2))
    IxR1 = (self.MRM) * (((self.MRR ** 2) / 4.0) + (self.FR - self.COM[2]) ** 2)
    IxR2 = (self.TRM) * ((self.TRR / 2.0) + (self.COM[2] ** 2))
    self.I[0] = IxS1 + IxS2 + IxS3 + IxR1 + IxR2
    
    IyS1 = (self.FM) * ((2.0 * self.FR / 5.0) + ((self.COM[0] ** 2) + (self.COM[2] ** 2)))
    IyS2 = (self.TBM) * (((3 * (self.TBR ** 2)) + (self.TBL ** 2))/12.0 + ((((self.TBL / 2.0) + self.FR + self.COM[0]) ** 2) + (self.COM[2] ** 2)))
    IyS3 = (self.RCM) * (((self.RCIR ** 2) + (self.RCOR ** 2))/2.0 + ((((self.TBL / 2.0) + self.FR + self.RCOR + self.COM[0]) ** 2) + (self.COM[2] ** 2)))
    IyR1 = (self.MRM) * (((self.MRR ** 2) / 4.0) + ((self.COM[0] ** 2) + ((self.FR - self.COM[2]) ** 2)))
    IyR2 = (self.TRM) * ((self.TRR / 2.0) + (((self.RCOR + self.TBL + self.FR + self.COM[0]) ** 2) + (self.COM[2] ** 2)))
    self.I[1] = IyS1 + IyS2 + IyS3 + IyR1 + IyR2
    
    IzS1 = (self.FM) * ((2.0 * self.FR / 5.0) + (self.COM[0] ** 2))
    IzS2 = (self.TBM) * ((((3 * (self.TBR ** 2)) + (self.TBL ** 2)) / 12.0) + (((self.TBL / 2.0) + self.FR + self.COM[0]) ** 2))
    IzS3 = (self.RCM) * ((( 3*(self.RCOR**2 + self.RCIR ** 2) + self.RCL ** 2)/12.0) + (((self.RCL / 2.0) + self.FR + self.RCOR + self.COM[0]) ** 2))
    IzR1 = (self.MRM) * (((self.MRR ** 2) / 4.0) + (self.COM[0] ** 2))
    IzR2 = (self.TRM) * ((self.TRR / 4.0) + ((self.RCOR + self.TBL + self.FR + self.COM[0]) ** 2))
    self.I[2] = IzS1 + IzS2 + IzS3 + IzR1 + IzR2
    
    # Initialize OriginToCOM transform
    self.OriginToCOMTransform = vtk.vtkMatrix4x4()
    for dim in range(3):
      self.OriginToCOMTransform.SetElement(dim, 3, self.COM[dim])
    self.OriginToCOMNode = slicer.vtkMRMLTransformNode()
    self.OriginToCOMNode.SetAndObserveMatrixTransformToParent(self.OriginToCOMTransform)
    self.OriginToCOMNode.SetName('OriginToCOM')
    slicer.mrmlScene.AddNode(self.OriginToCOMNode) 
    
    # Physics calculations will be performed on the COM, add observer to that node
    self.OriginToCOMNode.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, self.MoveModel)
    
    if CreateHeliAxesIsCheccked:
      self.HeliAxes = slicer.modules.createmodels.logic().CreateCoordinate(self.FR * 2, self.FR / 5.0)
      self.HeliAxes.SetName('HeliAxes')
      self.HeliAxes.ApplyTransform(self.OriginToCOMNode.GetTransformToParent())
      self.HeliAxes.HardenTransform()
    
    # COM to component transforms, to update model in space
    self.COMToFuselageMat = vtk.vtkMatrix4x4()
    self.COMToRotorMat = vtk.vtkMatrix4x4()
    self.COMToBoomMat = vtk.vtkMatrix4x4()
    self.COMToTailMat = vtk.vtkMatrix4x4()
    
  def MoveModel(self, caller, event): # Update model component positions based on change in COM location and orientation
    OriginToCOMMat = self.OriginToCOMNode.GetTransformToParent().GetMatrix()
    for dim in range(3):
      self.COM[dim] = OriginToCOMMat.GetElement(dim,3)
    
    OriginToFuselageMat = self.OriginToFuselageNode.GetTransformToParent().GetMatrix()
    print OriginToFuselageMat
    
    OriginToFuselageMat.Multiply4x4(OriginToCOMMat, self.COMToFuselageMat, OriginToFuselageMat)
    self.OriginToFuselageNode.SetAndObserveMatrixTransformToParent(OriginToFuselageMat)
    self.FuselageGeometricModel.SetAndObserveTransformNodeID(self.OriginToFuselageNode.GetID())
    
    OriginToBoomMat = self.OriginToBoomNode.GetTransformToParent().GetMatrix()
    OriginToBoomMat.Multiply4x4(OriginToCOMMat, self.COMToBoomMat, OriginToBoomMat)
    self.OriginToBoomNode.SetAndObserveMatrixTransformToParent(OriginToBoomMat)
    self.TailBoomGeometricModel.SetAndObserveTransformNodeID(self.OriginToBoomNode.GetID())
    
    OriginToTailRotorMat = self.OriginToBoomNode.GetTransformToParent().GetMatrix()
    OriginToTailRotorMat.Multiply4x4(OriginToCOMMat, self.COMToTailMat, OriginToTailRotorMat)
    self.OriginToTailRotorNode.SetAndObserveMatrixTransformToParent(OriginToTailRotorMat)
    self.TailRotorGeometricModel.SetAndObserveTransformNodeID(self.OriginToTailRotorNode.GetID())
    
    OriginToRotorMat = self.OriginToRotorNode.GetTransformToParent().GetMatrix()
    OriginToRotorMat.Multiply4x4(OriginToCOMMat, self.COMToRotorMat, OriginToRotorMat)
    self.OriginToRotorNode.SetAndObserveMatrixTransformToParent(OriginToRotorMat)
    self.MainRotorGeometricModel.SetAndObserveTransformNodeID(self.OriginToRotorNode.GetID())
    
    OriginToCylinderMat = self.OriginToCylinderNode.GetTransformToParent().GetMatrix()
    OriginToCylinderMat.Multiply4x4(OriginToCOMMat, self.COMToTailMat, OriginToCylinderMat)
    self.OriginToCylinderNode.SetAndObserveMatrixTransformToParent(OriginToCylinderMat)
    self.RotorCylinderGeometricModel.SetAndObserveTransformNodeID(self.OriginToCylinderNode.GetID())
    
    HeliAxes = slicer.util.getNode('HeliAxes')
    if HeliAxes != None:
      HeliAxes.SetAndObserveTransformNodeID(self.OriginToCOMNode.GetID())

    FuselageAxes = slicer.util.getNode('FuselageAxes')
    if FuselageAxes != None:
      FuselageAxes.SetAndObserveTransformNodeID(self.OriginToFuselageNode.GetID())
      RotorAxes = slicer.util.getNode('RotorAxes')
      RotorAxes.SetAndObserveTransformNodeID(self.OriginToRotorNode.GetID())
      RotorCylinderAxes = slicer.util.getNode('RotorCylinderAxes')
      RotorCylinderAxes.SetAndObserveTransformNodeID(self.OriginToCylinderNode.GetID())
      BoomAxes = slicer.util.getNode('BoomAxes')
      BoomAxes.SetAndObserveTransformNodeID(self.OriginToBoomNode.GetID())
      
    self.OriginToCOMNode.HardenTransform()
    self.UpdateHeliState()
  
  # Updates state of heli physical properties
  def UpdateHeliState(self):
    import math
    HeliOrientationPosMatrix = self.OriginToCOMNode.GetTransformToParent().GetMatrix()
  
    self.Forces[0] = (self.MainThrottle * self.MaxEnginePower * math.cos(self.CyclicTheta * self.Pi / 180.0) * math.sin(self.CyclicAlpha * self.Pi / 180.0)) + (self.Gravity * self.TotalMass * HeliOrientationPosMatrix.GetElement(2,0))
    self.Forces[1] = (self.MainThrottle * self.MaxEnginePower * math.sin(self.CyclicTheta * self.Pi / 180.0) * math.sin(self.CyclicAlpha * self.Pi / 180.0)) + (self.TailThrottle * self.MaxTailPower) + (self.Gravity * self.TotalMass * HeliOrientationPosMatrix.GetElement(2,1))
    self.Forces[2] = (self.MainThrottle * self.MaxEnginePower * math.cos(self.CyclicAlpha * self.Pi / 180.0)) + (self.Gravity * self.TotalMass * HeliOrientationPosMatrix.GetElement(2,2))
  
    #Displacement = [0, 0, 0]
    OriginToCOMMat = self.OriginToCOMNode.GetTransformToParent().GetMatrix()
    for dim in range(3):
      disp = (self.Velocity[dim] * self.dt) + ((1.0/2.0) * (self.Forces[dim] / self.TotalMass) * (self.dt**2))
      OriginToCOMMat.SetElement(dim, 3, disp)
    
    self.OriginToCOMNode.SetAndObserveMatrixTransformToParent(OriginToCOMMat)
    # MOMENTS MUST ALSO INCORPORATE DELTA_ANGULAR_MOMENTUM
    # Tail rotor moment arm currently an aproximation
    #self.Moments[0] = (self.TailThrottle * self.MaxTailPower) * (self.RCOR + self.TBL)
    #self.Moments[1] = ()
  #def UpdateForcesAndMoments(self):
    
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
    self.FuselageMassSlider.minimum = 100
    self.FuselageMassSlider.maximum = 2000
    self.FuselageMassSlider.value = 500
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
    self.TailMassSlider.minimum = 100
    self.TailMassSlider.maximum = 2000
    self.TailMassSlider.value = 200
    self.TailMassSlider.setToolTip("Set tail boom mass.")
    parametersFormLayout.addRow("Tail Boom Mass", self.TailMassSlider)
    
    self.TailRadiusSlider = ctk.ctkSliderWidget()
    self.TailRadiusSlider.singleStep = 0.05
    self.TailRadiusSlider.minimum = 0.1
    self.TailRadiusSlider.maximum = 1
    self.TailRadiusSlider.value = 0.3
    self.TailRadiusSlider.setToolTip("Set tail boom radius.")
    parametersFormLayout.addRow("Tail Boom Radius", self.TailRadiusSlider)
    
    self.TailLengthSlider = ctk.ctkSliderWidget()
    self.TailLengthSlider.singleStep = 0.05
    self.TailLengthSlider.minimum = 0.5
    self.TailLengthSlider.maximum = 5
    self.TailLengthSlider.value = 2
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
    self.RotorCylinderLengthSlider.value = 0.3
    self.RotorCylinderLengthSlider.setToolTip("Set rotor cylinder length.")
    parametersFormLayout.addRow("Rotor Cylinder Length", self.RotorCylinderLengthSlider)
    
    self.RotorCylinderInnerRadiusSlider = ctk.ctkSliderWidget()
    self.RotorCylinderInnerRadiusSlider.singleStep = 0.01
    self.RotorCylinderInnerRadiusSlider.minimum = 0.05
    self.RotorCylinderInnerRadiusSlider.maximum = 1
    self.RotorCylinderInnerRadiusSlider.value = 0.4
    self.RotorCylinderInnerRadiusSlider.setToolTip("Set rotor inner radius (must be larger than tail fan radius).")
    parametersFormLayout.addRow("Rotor Cylinder Inner Radius", self.RotorCylinderInnerRadiusSlider)

    self.RotorCylinderOuterRadiusSlider = ctk.ctkSliderWidget()
    self.RotorCylinderOuterRadiusSlider.singleStep = 0.01
    self.RotorCylinderOuterRadiusSlider.minimum = 0.3
    self.RotorCylinderOuterRadiusSlider.maximum = 1.5
    self.RotorCylinderOuterRadiusSlider.value = 0.5
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
    self.MainRotorRadiusSlider.value = 3
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
    
    #
    # Start button
    #
    self.StartButton = qt.QPushButton("Start")
    self.StartButton.toolTip = "Start the auto-pilot simulation"
    self.StartButton.enabled = True
    parametersFormLayout.addRow(self.StartButton)

    # connections
    self.BuildButton.connect('clicked(bool)', self.onBuildButton)
    self.StartButton.connect('clicked(bool)', self.onStartButton)

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
    self.HelicopterModel = Logic.BuildModel(FuselageMass, FuselageRadius, TailBoomMass, TailBoomLength, TailBoomRadius, RotorCylinderMass, RotorCylinderLength, \
      RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorMass, MainRotorRadius, TailRotorMass, TailRotorRadius, self.CreateComponentAxesCheckBox.checked, self.CreateHelicopterAxesCheckBox.checked)

  def onStartButton(self):
    self.HelicopterModel.UpdateHeliState()
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

  def BuildModel(self, FuselageMass, FuselageRadius, TailBoomMass, TailBoomLength, TailBoomRadius, RotorCylinderMass, RotorCylinderLength, RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorMass, MainRotorRadius, TailRotorMass, TailRotorRadius, CreateComponentAxesIsChecked, CreateHelicopterAxesIsChecked):
    """
    Build helicopter model
    """

    HelicopterModel = Helicopter('Heli')
    HelicopterModel.Build(FuselageMass, FuselageRadius, TailBoomMass, TailBoomLength, TailBoomRadius, RotorCylinderMass, RotorCylinderLength,\
      RotorCylinderInnerRadius, RotorCylinderOuterRadius, MainRotorMass, MainRotorRadius, TailRotorMass, TailRotorRadius, CreateComponentAxesIsChecked, CreateHelicopterAxesIsChecked)

    return HelicopterModel

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
