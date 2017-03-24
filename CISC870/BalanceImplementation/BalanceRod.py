import csv, math
import numpy as np
import matplotlib as mpl

class FuzzyLogic():
  #def __init__(self)
  import numpy as np
  
  class Trapezoid():                            # Reduces to triangle when LS = RS
    def __init__(self, LF, LS, RS, RF):         # Points are of the form (x,mu) where mu is membership, 0 at feet and 1 at shoulders
      # Left being lesser in x than the right
      self.LeftFoot = LF
      self.LeftShoulder = LS
      self.RightShoulder = RS
      self.RightFoot = RF
      
      # Can break truncated (by membership value) trapezoid down into these sections
      self.LeftTriangleArea = 0
      self.CenterRectangleArea = 0
      self.RightTriangleArea = 0
      self.Area = 0
      self.COA = 0    # Center of area
      
      self.Membership = 0
      
    def ComputeMembership(self, CrispValue):
      if CrispValue < self.LeftFoot[0]:
        self.Membership = 0
        return
        
      if CrispValue >= self.LeftFoot[0] and CrispValue < self.LeftShoulder[0]:
        slope = (self.LeftShoulder[1] - self.LeftFoot[1]) / (self.LeftShoulder[0] - self.LeftFoot[0])
        self.Membership = self.LeftFoot[1] + (slope * (CrispValue - self.LeftFoot[0]))
        self.LeftTriangleArea = (1.0/2.0) * (CrispValue - self.LeftFoot[0]) * (self.Membership)
        self.RightTriangleArea = (1.0/2.0) * ((self.Membership / 1.0) * (self.RightFoot[0] - self.RightShoulder[0])) * self.Membership
        self.CenterRectangleArea = self.Membership * ((self.RightFoot[0] - self.LeftFoot[0]) - (CrispValue - self.LeftFoot[0]) - ((self.Membership / 1.0) * (self.RightFoot[0] - self.RightShoulder[0])))
        return
        
      if CrispValue >= self.LeftShoulder[0] and CrispValue < self.RightShoulder[0]:
        self.Membership = 1.0
        self.LeftTriangleArea = (1.0/2.0) * (self.LeftShoulder[0] - self.LeftFoot[0]) * (self.Membership)
        self.RightTriangleArea = (1.0/2.0) * (self.RightFoot[0] - self.RightShoulder[0]) * (self.Membership)
        self.CenterRectangleArea = self.Membership * (self.RightShoulder[0] - self.LeftShoulder[0])
        return
        
      if CrispValue >= self.RightShoulder[0] and CrispValue < self.RightFoot[0]:
        slope = (self.RightFoot[1] - self.RightShoulder[1]) / (self.RightFoot[0] - self.RightShoulder[0])
        self.Membership = self.LeftFoot[1] + (slope * (CrispValue - self.LeftFoot[0]))
        self.LeftTriangleArea = (1.0/2.0) * ((self.Membership / 1.0) * (self.LeftShoulder[0] - self.LeftFoot[0])) * self.Membership
        self.RightTriangleArea = (1.0/2.0) * (self.RightFoot[0] - CrispValue) * (self.Membership)
        self.CenterRectangleArea = self.Membership * ((self.RightFoot[0] - self.LeftFoot[0]) - (CrispValue - self.LeftFoot[0]) - ((self.Membership / 1.0) * (self.RightFoot[0] - self.RightShoulder[0])))
        return
        
      if CrispValue > self.RightFoot[0]:
        self.Membership = 0
        return
        
    def ComputeArea(self):
      # Uses truncation of membership function
      if self.LeftFoot[0] == self.LeftShoulder[0]:
        self.LeftTriangleArea = 0
      else:
        
      self.Area = self.LeftTriangleArea + self.CenterRectangleArea + self.RightTriangleArea 
      self.ComputeCenterOfArea()
  
    def ComputeCenterOfArea(self):
      LeftTriangleCenter = self.LeftFoot[0] + ((2.0/3.0) * (self.Membership / 1.0) * (self.LeftShoulder[0] - self.LeftFoot[0]))
      RightTriangleCenter = self.RightShoulder[0] + ((1.0/3.0) * ((1.0 - self.Membership) / 1.0) * (self.RightFoot [0] - self.RightShoulder[0]))
      CenterRectangleCenter = (((self.RightShoulder[0] + (1.0 - self.Membership) / 1.0) * (self.RightFoot [0] - self.RightShoulder[0])) + (self.LeftFoot[0] + (self.Membership / 1.0) * (self.LeftShoulder[0] - self.LeftFoot[0])))/2.0
      self.COA = ((self.LeftTriangleArea * LeftTriangleCenter) + (self.CenterRectangleArea * CenterRectangleCenter) + (self.RightTriangleArea * RightTriangleCenter)) / (self.LeftTriangleArea + self.CenterRectangleArea + self.RightTriangleArea)
    
    def PrintMembershipFunction(self, OutputDir, ImageName):
      import numpy as np
      import matplotlib.pyplot as plt
      PointsPerSegment = 50
      
      # Start with complete membership function, highlight actual value after
      LeftSlopeDomain = np.linspace(self.LeftFoot[0], self.LeftShoulder[0], PointsPerSegment)
      LeftSlopeRange = np.linspace(0, 1, PointsPerSegment)
      PlateauDomain = np.linspace(self.LeftShoulder[0], self.RightShoulder[0], PointsPerSegment)
      PlateauRange = np.linspace(1, 1, PointsPerSegment)
      RightSlopeDomain = np.linspace(self.RightShoulder[0], self.RightFoot[0], PointsPerSegment)
      RightSlopeRange = np.linspace(1, 0, PointsPerSegment)
      ax = plt.axes()
      ax.plot(LeftSlopeDomain, LeftSlopeRange, 'k.', markersize=3)
      ax.plot(PlateauDomain, PlateauRange, 'k.', markersize=3)
      ax.plot(RightSlopeDomain, RightSlopeRange, 'k.', markersize=3)
      plt.show()
        
  # Recursively defined Conjunction (and Disjunction) allow multiple rules or sets to be combined
  def FuzzyConjunction(self, Memberships, tNorm):
    if tNorm == 'min':
      if len(Memberships) > 1:
        return min(Memberships[0], self.FuzzyConjunction(Memberships[1:], 'min'))
      else:
        return Memberships[0]
    else:
      print("Error - Unknown t-norm passed for FuzzyConjunction")
      return
      
  def FuzzyDisjunction(self, Memberships, sNorm):
    if sNorm == "max":
      if len(Memberships) > 1:
        return max(Memberships[0], self.FuzzyDisjunction(Memberships[1:], 'max'))
      else:
        return Memberships[0]
    else:
      print("Error - Unknown s-norm passed for FuzzyDisjunction")
      return
      
  def FuzzyImplication(self, AntecedantMembership, ConsequentMembership, Method):
    if Method == "KD":
      return max(1 - AntecedantMembership, ConsequentMembership)
    else:
      print("Error - Unknown FuzzyImplication method")
      return
        
class BalanceBot():
  def __init__(self, BM, BMF, RL, RM):
    self.FL = FuzzyLogic()
    self.OutputDir = './/Output//'
    
    self.Gravity = 9.81
    self.Time = 0       # Start time, may be used to plot robot responses
    self.dt = 0.25      # Time increment (sec)
    self.RodDragCoefficient = 10    # Force (per rod length - wind speed) in N
    
    # Robot properties
    self.BotMass = BM         # (kg)
    self.BotMaxForce = BMF    # Maximum force with which bot can accelerate in either direction (N)
    self.RodLength = RL
    self.RodMass = RM
    self.RodMomentOfInertia = self.RodMass * (self.RodLength ** 2) / 3.0
    
    # Initial robot state
    self.MotorForce = 0 # Ranges from -BMF to +BMF --- this is output from fuzzy logic
    self.Position = 0   # Start at origin, can move back and forth, units are meters
    self.Velocity = 0
    self.Acceleration = 0
    
    self.Tilt = 10      # Rod starts upright (deg)
    self.AngularVelocity = (np.random.uniform() - 0.5) * 30            # Start with some initial angular velocity to necessitate adjustment
    self.AngularAcceleration = 0
    
    self.WindSpeed = (np.random.uniform() - 0.5) * 2                 # Will exert external force on robot and rod
    
    # Properties for plotting bot
    self.BotSize = 0.1            # Bot size (width and height, square bot) in meters for plotting
    
    # Fuzzy sets
    self.PosTiltErrorLarge = self.FL.Trapezoid((20,0), (40,1), (90,1), (90,0))
    self.PosTiltErrorMed = self.FL.Trapezoid((0,0), (20,1), (20,1), (40,0))
    self.PosTiltErrorSmall = self.FL.Trapezoid((0,0), (0,1), (0,1), (20,0))

    self.PosWindHigh = self.FL.Trapezoid((0.5,0), (1,1), (1,1), (1,0))            
    self.PosWindMed = self.FL.Trapezoid((0,0), (0.5,1), (0.5,1), (1,0))                   # Wind speed into direction of tilt; helping wind is always Low
    self.PosWindLow = self.FL.Trapezoid((0,0), (0,1), (0,1), (0.5,0))                 
    
    self.PosMotorResponseLow = self.FL.Trapezoid((0,0), (0,1), (0,1), (0.25,0))
    self.PosMotorResponseMedLow = self.FL.Trapezoid((0,0), (0.25,1), (0.25,1), (0.5,0))
    self.PosMotorResponseMed = self.FL.Trapezoid((0.25,0), (0.5,1), (0.5,1), (0.75,0))
    self.PosMotorResponseMedHigh = self.FL.Trapezoid((0.5,0), (0.75,1), (0.75,1), (1,0))
    self.PosMotorResponseHigh = self.FL.Trapezoid((0.75, 0), (1,1), (1, 1), (1,0))

    self.NegTiltErrorLarge = self.FL.Trapezoid((-20, 0), (-40,1), (-40, 1), (-40,0))
    self.NegTiltErrorMed = self.FL.Trapezoid((0,0), (-20,1), (-20,1), (-40,0))
    self.NegTiltErrorSmall = self.FL.Trapezoid((0,0), (0,1), (0,1), (-20, 0))
    
    self.NegWindHigh = self.FL.Trapezoid((-0.5, 0), (-1, 1), (-1, 1), (-1, 0))            
    self.NegWindMed = self.FL.Trapezoid((0,0), (-0.5,1), (-0.5,1), (-1,0))      
    self.NegWindLow = self.FL.Trapezoid((0,0), (0, 1), (0,1), (-0.5, 0))    
    
    self.NegMotorResponseLow = self.FL.Trapezoid((0,0), (0,1), (0,1), (0.25,0))
    self.NegMotorResponseMedLow = self.FL.Trapezoid((0,0), (0.25,1), (0.25,1), (0.5,0))
    self.NegMotorResponseMed = self.FL.Trapezoid((0.25,0), (0.5,1), (0.5,1), (0.75,0))
    self.NegMotorResponseMedHigh = self.FL.Trapezoid((0.5,0), (0.75,1), (0.75,1), (1,0))
    self.NegMotorResponseHigh = self.FL.Trapezoid((0.75, 0), (1, 1), (1, 1), (1, 0))
       
  def DrawBotToFile(self, FileName):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    ax = plt.axes()
    
    # Draw bot body as patch, and balance rod as arrow
    BotPatch = patches.Rectangle((self.Position - (self.BotSize / 2.0), 0), self.BotSize, self.BotSize, linewidth = 1, edgecolor = 'k', facecolor = 'k')
    ax.add_patch(BotPatch)
    ax.arrow(self.Position, self.BotSize, self.RodLength * np.cos((90 - self.Tilt) * np.pi / 180.0), self.RodLength * np.sin((90 - self.Tilt) * np.pi / 180.0), linewidth = 3, head_width = 0.05, head_length=0.05, fc='k')
    
    # Annotate with wind speed arrow
    ax.arrow(0.5, 0.9, self.WindSpeed / 2.0, 0, linewidth = 3, head_width = 0.05, head_length=0.05, ec = 'g', fc='g')
    ax.text(0.4, 0.95, 'Wind Speed: ' + str(self.WindSpeed)[:5], color='g')
    plt.axis([-1, 1, 0, 1])
    plt.savefig(self.OutputDir + FileName)
    ax.clear()
    
  def UpdateFuzzySets(self):
    RelativeWind = self.WindSpeed - self.Velocity
    ImplicationMethod = 'KD'
    tNorm = 'min'
    sNorm = 'max'
    
    # ------- Positive direction sets - CW rotations, right-wards translation ------- #
    self.PosTiltErrorLarge.ComputeMembership(self.Tilt)
    self.PosTiltErrorMed.ComputeMembership(self.Tilt)
    self.PosTiltErrorSmall.ComputeMembership(self.Tilt)
    
    self.PosWindHigh.ComputeMembership(RelativeWind)
    self.PosWindMed.ComputeMembership(RelativeWind)
    self.PosWindLow.ComputeMembership(RelativeWind)
    
    # (Re)initialize MotorResponseRules
    PosOutputLowRules = [0, 0]
    PosOutputMedLowRules = [0]
    PosOutputMedRules = [0, 0,]
    PosOutputMedHighRules = [0, 0]
    PosOutputHighRules = [0, 0]
    
    # TiltErrorSmall and WindLow --> MotorResponseMagnitudeLow
    PosOutputLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorSmall and WindMed --> MotorResponseMagnitudeLow
    PosOutputLowRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseLow.Membership = self.FL.FuzzyDisjunction(PosOutputLowRules, sNorm)
    
    # TiltErrorSmall and WindHigh --> MotorResponseMagnitudeMed
    PosOutputMedLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(PosOutputMedLowRules, sNorm)
    
    # TiltErrorMed and WindLow --> MotorResponseMagnitudeMed
    PosOutputMedRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorMed and WindMed --> MotorResponseMagnitudeMed
    PosOutputMedRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMed.Membership = self.FL.FuzzyDisjunction(PosOutputMedRules, sNorm)
    
    # TiltErrorMed and WindHigh --> MotorResponseMagnitudeMedHigh
    PosOutputMedHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindLow --> MotorResponseMagnitudeMedHigh
    PosOutputMedHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(PosOutputMedHighRules, sNorm)
    
    # TiltErrorLarge and WindMed --> MotorResponseMagnitudeHigh
    PosOutputHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    PosOutputHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseHigh.Membership = self.FL.FuzzyDisjunction(PosOutputHighRules, sNorm)
    
    self.PosMotorResponseLow.ComputeArea()
    self.PosMotorResponseMedLow.ComputeArea()
    self.PosMotorResponseMed.ComputeArea()
    self.PosMotorResponseMedHigh.ComputeArea()
    self.PosMotorResponseHigh.ComputeArea()
    
    # ------- Negative direction sets - CCW rotations, left-wards translation ------- #
    self.NegTiltErrorLarge.ComputeMembership(self.Tilt)
    self.NegTiltErrorMed.ComputeMembership(self.Tilt)
    self.NegTiltErrorSmall.ComputeMembership(self.Tilt)
    
    self.NegWindHigh.ComputeMembership(RelativeWind)
    self.NegWindMed.ComputeMembership(RelativeWind)
    self.NegWindLow.ComputeMembership(RelativeWind)
    
    # (Re)initialize MotorResponseRules
    NegOutputLowRules = [0, 0]
    NegOutputMedLowRules = [0]
    NegOutputMedRules = [0, 0,]
    NegOutputMedHighRules = [0, 0]
    NegOutputHighRules = [0, 0]
    
    # TiltErrorSmall and WindLow --> MotorResponseMagnitudeLow
    NegOutputLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorSmall and WindMed --> MotorResponseMagnitudeLow
    NegOutputLowRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.NegMotorResponseLow.Membership = self.FL.FuzzyDisjunction(NegOutputLowRules, sNorm)
    
    # TiltErrorSmall and WindHigh --> MotorResponseMagnitudeMed
    NegOutputMedLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(PosOutputMedLowRules, sNorm)
    
    # TiltErrorMed and WindLow --> MotorResponseMagnitudeMed
    NegOutputMedRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorMed and WindMed --> MotorResponseMagnitudeMed
    NegOutputMedRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMed.Membership = self.FL.FuzzyDisjunction(PosOutputMedRules, sNorm)
    
    # TiltErrorMed and WindHigh --> MotorResponseMagnitudeMedHigh
    NegOutputMedHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindLow --> MotorResponseMagnitudeMedHigh
    NegOutputMedHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(PosOutputMedHighRules, sNorm)
    
    # TiltErrorLarge and WindMed --> MotorResponseMagnitudeHigh
    NegOutputHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    NegOutputHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    self.NegMotorResponseHigh.Membership = self.FL.FuzzyDisjunction(NegOutputHighRules, sNorm)
    
    self.NegMotorResponseLow.ComputeArea()
    self.NegMotorResponseMedLow.ComputeArea()
    self.NegMotorResponseMed.ComputeArea()
    self.NegMotorResponseMedHigh.ComputeArea()
    self.NegMotorResponseHigh.ComputeArea()
  
  def UpdateControls(self):
    import numpy as np
    # Use Center of Mass method
    NegMotorResponses = [self.NegMotorResponseLow.Area, self.NegMotorResponseMedLow.Area, self.NegMotorResponseMed.Area, self.NegMotorResponseMedHigh.Area, self.NegMotorResponseHigh.Area]
    PosMotorResponses = [self.PosMotorResponseLow.Area, self.PosMotorResponseMedLow.Area, self.PosMotorResponseMed.Area, self.PosMotorResponseMedHigh.Area, self.PosMotorResponseHigh.Area]
    if sum(NegMotorResponses) > sum(PosMotorResponses):
      # Resolve to move in negative direction, but how fast?
      TotalSetMass = self.NegMotorResponseLow.Area + self.NegMotorResponseMedLow.Area + self.NegMotorResponseMed.Area + self.NegMotorResponseMedHigh.Area + self.NegMotorResponseHigh.Area
      self.MotorForce = self.BotMaxForce * ((self.NegMotorResponseLow.Area * self.NegMotorResponseLow.COA) + (self.NegMotorResponseMedLow.Area * self.NegMotorResponseMedLow.COA) + (self.NegMotorResponseMed.Area * self.NegMotorResponseMed.COA) + (self.NegMotorResponseMedHigh.Area * self.NegMotorResponseMedHigh.COA) + (self.NegMotorResponseHigh.Area * self.NegMotorResponseHigh.COA)) / (TotalSetMass)
      
    else:   # Move in positive direction
      TotalSetMass = self.PosMotorResponseLow.Area + self.PosMotorResponseMedLow.Area + self.PosMotorResponseMed.Area + self.PosMotorResponseMedHigh.Area + self.PosMotorResponseHigh.Area
      self.MotorForce = self.BotMaxForce * ((self.PosMotorResponseLow.Area * self.PosMotorResponseLow.COA) + (self.PosMotorResponseMedLow.Area * self.PosMotorResponseMedLow.COA) + (self.PosMotorResponseMed.Area * self.PosMotorResponseMed.COA) + (self.PosMotorResponseMedHigh.Area * self.PosMotorResponseMedHigh.COA) + (self.PosMotorResponseHigh.Area * self.PosMotorResponseHigh.COA)) / (TotalSetMass)
  
  def UpdateMechanicalState(self):
    RelativeWind = self.WindSpeed - self.Velocity
    
    self.Acceleration = self.MotorForce / self.BotMass
    self.Position += 0.5 * (self.Acceleration) * (self.dt ** 2)
    self.Velocity += self.Acceleration * self.dt
    
    # Start with BalanceRod - experiences torques from gravity, bot acceleration, and wind 
    GravitationalTorque = self.Gravity * self.RodMass * np.cos(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    AccelerationTorque = self.Acceleration * self.RodMass * np.sin(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    WindTorque = RelativeWind * self.RodLength * np.sin(self.Tilt * np.pi / 180.0) * self.RodDragCoefficient * (self.RodLength/2.0)
    RodTorque = GravitationalTorque + AccelerationTorque + WindTorque
    
    #print(GravitationalTorque, AccelerationTorque)
    self.AngularAcceleration = RodTorque / self.RodMomentOfInertia
    self.Tilt += 0.5 * self.AngularAcceleration * (self.dt ** 2)
    self.AngularVelocity += self.AngularAcceleration * self.dt
    
    
  def StartBalancing(self):
    self.UpdateMechanicalState()
    self.UpdateFuzzySets()
    self.UpdateControls()


    
Bot = BalanceBot(10, 10, 0.2, 1)
#Bot.StartBalancing()
#Bot.PosTiltErrorLarge.PrintMembershipFunction('.\\', 'Membership.png')


for RotTest in range(100):
  Bot.StartBalancing()
  Bot.DrawBotToFile('test' + str(RotTest) + '.png')

