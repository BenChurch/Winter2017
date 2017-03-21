import csv, math
import numpy as np
import matplotlib as mpl

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

  # Recursively defined Conjunction (and Disjunction) allow multiple rules or sets to be combined
  def FuzzyConjunction(self, Memberships, tNorm):
    if tNorm == 'min':
      if len(Memberships) > 1:
        return min(Memberships[0], self.FuzzyConjunction(Memberships[1:]), 'min')
      else:
        return Memberships[0]
    else:
      print("Error - Unknown t-norm passed for FuzzyConjunction")
      return
      
  def FuzzyDisjunction(self, Memberships, sNorm):
    if sNorm == "max":
      if len(Memberships) > 1:
        return max(Memberships[0], self.FuzzyDisjunction(Memberships[1:]), 'max')
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
    self.PosTiltErrorLarge = self.FL.UnboundedTrap((20, 0), (40, 1))
    self.PosTiltErrorMed = self.FL.BoundedTrap(0, 20, 20, 40)
    self.PosTiltErrorSmall = self.FL.UnboundedTrap((0, 1), (20, 0))

    self.PosWindHigh = self.FL.UnboundedTrap((0.5, 0), (1.0, 1.0))            
    self.PosWindMed = self.FL.BoundedTrap(0, 0.5, 0.5, 1)                   # Wind speed into direction of tilt; helping wind is always Low
    self.PosWindLow = self.FL.UnboundedTrap((0, 1), (0.5, 0))                 
    
    self.PosMotorResponseLow = self.FL.UnboundedTrap((0,1), (0.25,0))
    self.PosMotorResponseMedLow = self.FL.BoundedTrap(0, 0.25, 0.25, 0.5)
    self.PosMotorResponseMed = self.FL.BoundedTrap(0.25, 0.5, 0.5, 0.75)
    self.PosMotorResponseMedHigh = self.FL.BoundedTrap(0.5, 0.75, 0.75, 1)
    self.PosMotorResponseHigh = self.FL.UnboundedTrap((0.75, 0), (1, 1))

    self.NegTiltErrorLarge = self.FL.UnboundedTrap((-20, 0), (-40, 1))
    self.NegTiltErrorMed = self.FL.BoundedTrap(0, -20, -20, -40)
    self.NegTiltErrorSmall = self.FL.UnboundedTrap((0, 1), (-20, 0))
    
    self.NegWindHigh = self.FL.UnboundedTrap((-0.5, 0), (-1.0, 1.0))            
    self.NegWindMed = self.FL.BoundedTrap(0, -0.5, -0.5, -1)      
    self.NegWindLow = self.FL.UnboundedTrap((0, 1), (-0.5, 0))    
    
    self.NegMotorResponseLow = self.FL.UnboundedTrap((0,1), (0.25,0))
    self.NegMotorResponseMedLow = self.FL.BoundedTrap(0, 0.25, 0.25, 0.5)
    self.NegMotorResponseMed = self.FL.BoundedTrap(0.25, 0.5, 0.5, 0.75)
    self.NegMotorResponseMedHigh = self.FL.BoundedTrap(0.5, 0.75, 0.75, 1)
    self.NegMotorResponseHigh = self.FL.UnboundedTrap((0.75, 0), (1, 1))
       
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
    self.TiltErrorLarge.ComputeMembership(self.Tilt)
    self.TiltErrorMed.ComputeMembership(self.Tilt)
    self.TiltErrorSmall.ComputeMembership(self.Tilt)
    
    RelativeWind = self.WindSpeed - self.Velocity
    self.WindHigh.ComputeMembership(RelativeWind)
    self.WindMed.ComputeMembership(RelativeWind)
    self.WindLow.ComputeMembership(RelativeWind)
    
    # (Re)initialize MotorResponseRules
    PosOutputLowRules = [0, 0]
    PosOutputMedLowRules = [0]
    PosOutputMedRules = [0, 0,]
    PosOutputMedHighRules = [0, 0]
    PosOutputHighRules = [0, 0]
    
    
    # ------- Positive direction sets - CW rotations, right-wards translation ------- #
    
    # TiltErrorSmall and WindLow --> MotorResponseMagnitudeLow
    PosOutputLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorSmall.Membership, self.PosWindLow.Membership), 1)
    
    # TiltErrorSmall and WindMed --> MotorResponseMagnitudeLow
    PosOutputLowRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorSmall.Membership, self.PosWindMed.Membership), 1)
    
    self.PosMotorResponseLow.Membership = self.FL.FuzzyDisjunction(PosOutputLowRules)
    
    # TiltErrorSmall and WindHigh --> MotorResponseMagnitudeMed
    PosOutputMedLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorSmall.Membership, self.PosWindHigh.Membership), 1)
    
    self.PosMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(PosOutputMedLowRules)
    
    # TiltErrorMed and WindLow --> MotorResponseMagnitudeMed
    PosOutputMedRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorMed.Membership, self.PosWindLow.Membership), 1)
    
    # TiltErrorMed and WindMed --> MotorResponseMagnitudeMed
    PosOutputMedRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorMed.Membership, self.PosWindMed.Membership), 1)
    
    self.PosMotorResponseMed.Membership = self.FL.FuzzyDisjunction(PosOutputMedRules)
    
    # TiltErrorMed and WindHigh --> MotorResponseMagnitudeMedHigh
    PosOutputMedHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorMed.Membership, self.PosWindHigh.Membership), 1)
    
    # TiltErrorLarge and WindLow --> MotorResponseMagnitudeMedHigh
    PosOutputMedHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorLarge.Membership, self.PosWindLow.Membership), 1)
    
    self.PosMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(PosOutputMedHighRules)
    
    # TiltErrorLarge and WindMed --> MotorResponseMagnitudeHigh
    PosOutputHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorLarge.Membership, self.PosWindMed.Membership), 1)
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    PosOutputHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.PosTiltErrorLarge.Membership, self.PosWindHigh.Membership), 1)
    
    self.PosMotorResponseHigh.Membership = self.FL.FuzzyDisjunction(PosOutputHighRules)
    
    # ------- Negative direction sets - CCW rotations, left-wards translation ------- #

    # TiltErrorSmall and WindLow --> MotorResponseMagnitudeLow
    NegOutputLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorSmall.Membership, self.NegWindLow.Membership), 1)
    
    # TiltErrorSmall and WindMed --> MotorResponseMagnitudeLow
    NegOutputLowRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorSmall.Membership, self.NegWindMed.Membership), 1)
    
    self.NegMotorResponseLow.Membership = self.FL.FuzzyDisjunction(NegOutputLowRules)
    
    # TiltErrorSmall and WindHigh --> MotorResponseMagnitudeMed
    NegOutputMedLowRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorSmall.Membership, self.NegWindHigh.Membership), 1)
    
    self.PosMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(PosOutputMedLowRules)
    
    # TiltErrorMed and WindLow --> MotorResponseMagnitudeMed
    NegOutputMedRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorMed.Membership, self.NegWindLow.Membership), 1)
    
    # TiltErrorMed and WindMed --> MotorResponseMagnitudeMed
    NegOutputMedRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorMed.Membership, self.NegWindMed.Membership), 1)
    
    self.PosMotorResponseMed.Membership = self.FL.FuzzyDisjunction(PosOutputMedRules)
    
    # TiltErrorMed and WindHigh --> MotorResponseMagnitudeMedHigh
    NegOutputMedHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorMed.Membership, self.NegWindHigh.Membership), 1)
    
    # TiltErrorLarge and WindLow --> MotorResponseMagnitudeMedHigh
    NegOutputMedHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorLarge.Membership, self.NegWindLow.Membership), 1)
    
    self.PosMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(PosOutputMedHighRules)
    
    # TiltErrorLarge and WindMed --> MotorResponseMagnitudeHigh
    NegOutputHighRules[0] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorLarge.Membership, self.NegWindMed.Membership), 1)
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    NegOutputHighRules[1] = self.FL.FuzzyImplication(self.FL.FuzzyConjunction(self.NegTiltErrorLarge.Membership, self.NegWindHigh.Membership), 1)
    
    self.NegMotorResponseHigh.Membership = self.FL.FuzzyDisjunction(NegOutputHighRules)
    
    
  #def UpdateControls(self):
    #self.MotorForce = self.Defuzzify
  
  def UpdateMechanicalState(self):
    # Start with BalanceRod
    GravitationalTorque = self.Gravity * self.RodMass * np.cos(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    AccelerationTorque = self.Acceleration * self.RodMass * np.sin(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    RelativeWind = self.WindSpeed - self.Velocity
    
    RodTorque = GravitationalTorque + AccelerationTorque
    #print(GravitationalTorque, AccelerationTorque)
    self.AngularAcceleration = RodTorque / self.RodMomentOfInertia
    self.Tilt += 0.5 * self.AngularAcceleration * (self.dt ** 2)
    self.AngularVelocity += self.AngularAcceleration * self.dt
    
    
  def StartBalancing(self):
    self.UpdateFuzzySets()
    #self.UpdateControls()
    #self.UpdateMechanicalState()
    
Bot = BalanceBot(10, 10, 0.2, 1)
for RotTest in range(100):
  Bot.UpdateMechanicalState()
  Bot.DrawBotToFile('test' + str(RotTest) + '.png')