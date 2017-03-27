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
      self.COA = None    # Center of area - remains None for later checks in defuzzification
      
      self.CrispValue = 0 # Keep this from each membership value recomputation - useful in fuzzy set geometry
      self.Membership = 0
      
    def ComputeMembership(self, CV):
      self.CrispValue = CV
      #if self.CrispValue > 0:
      if self.CrispValue < self.LeftFoot[0]:
        self.Membership = 0
        self.COA = None
        return
        
      if self.CrispValue >= self.LeftFoot[0] and self.CrispValue < self.LeftShoulder[0]:
        slope = (self.LeftShoulder[1] - self.LeftFoot[1]) / (self.LeftShoulder[0] - self.LeftFoot[0])
        self.Membership = self.LeftFoot[1] + (slope * (self.CrispValue - self.LeftFoot[0]))
        return
        
      if self.CrispValue >= self.LeftShoulder[0] and self.CrispValue < self.RightShoulder[0]:
        self.Membership = 1.0
        return
        
      if self.CrispValue >= self.RightShoulder[0] and self.CrispValue < self.RightFoot[0]:
        slope = (self.RightFoot[1] - self.RightShoulder[1]) / (self.RightFoot[0] - self.RightShoulder[0])
        self.Membership = self.RightFoot[1] + (slope * (self.CrispValue - self.RightFoot[0]))
        return
        
      if self.CrispValue > self.RightFoot[0]:
        self.Membership = 0
        self.COA = None
        return
      
     # else:  # If self.CrispValue < 0
    
    def ComputeArea(self):
      # Uses truncation of membership function
      if self.LeftFoot[0] == self.LeftShoulder[0]:
        LeftTriangleBase = 0
        self.LeftTriangleArea = 0
      else:
        LeftTriangleBase = self.Membership*(self.LeftShoulder[0] - self.LeftFoot[0])/(self.LeftShoulder[1] - self.LeftFoot[1])    #self.LeftShoulder[1] - self.LeftFoot[1] == 1 - 0, assumedly
        self.LeftTriangleArea = (1.0/2.0) * (self.Membership) * (LeftTriangleBase)
      if self.RightFoot[0] == self.RightShoulder[0]:
        RightTriangleBase = 0
        self.RightTriangleArea = 0
      else:
        RightTriangleBase = self.Membership * (self.RightFoot[0] - self.RightShoulder[0]) / (self.RightShoulder[1] - self.RightFoot[1])
        self.RightTriangleArea = (1.0/2.0) * self.Membership * RightTriangleBase
      self.CenterRectangleArea = ((self.RightFoot[0] - self.LeftFoot[0]) - (LeftTriangleBase) - (RightTriangleBase)) * self.Membership
      self.Area = self.LeftTriangleArea + self.CenterRectangleArea + self.RightTriangleArea
      self.ComputeCenterOfArea()
  
    def ComputeCenterOfArea(self):
      LeftTriangleCenter = self.LeftFoot[0] + ((2.0/3.0) * (self.Membership / 1.0) * (self.LeftShoulder[0] - self.LeftFoot[0]))
      RightTriangleCenter = self.RightFoot[0] - ((2.0/3.0) * (self.Membership / 1.0) * (self.RightFoot [0] - self.RightShoulder[0]))
      CenterRectangleCenter = ((self.RightFoot[0] - (self.Membership / 1.0) * (self.RightFoot [0] - self.RightShoulder[0])) + (self.LeftFoot[0] + (self.Membership / 1.0) * (self.LeftShoulder[0] - self.LeftFoot[0])))/2.0
      self.COA = ((self.LeftTriangleArea * LeftTriangleCenter) + (self.CenterRectangleArea * CenterRectangleCenter) + (self.RightTriangleArea * RightTriangleCenter)) / (self.LeftTriangleArea + self.CenterRectangleArea + self.RightTriangleArea)
    
    def PrintMembershipFunctionToAxes(self,  col, axes=None):
      # TODO overlay shape of actual membership solid lines onto possible membership dotted lines
      
      import numpy as np
      import matplotlib.pyplot as plt
      import matplotlib.lines as mlines
      PointsPerSegment = 50
      
      if axes == None:
        ax = plt.axes()
      else:
        ax = axes
      
      # Start with complete membership function, highlight actual value after
      LeftSlopeDomain = np.linspace(self.LeftFoot[0], self.LeftShoulder[0], PointsPerSegment)
      LeftSlopeRange = np.linspace(0, 1, PointsPerSegment)
      PlateauDomain = np.linspace(self.LeftShoulder[0], self.RightShoulder[0], PointsPerSegment/2)
      PlateauRange = np.ones(int(PointsPerSegment/2))
      RightSlopeDomain = np.linspace(self.RightShoulder[0], self.RightFoot[0], PointsPerSegment)
      RightSlopeRange = np.linspace(1, 0, PointsPerSegment)
      
      
      ax.plot(LeftSlopeDomain, LeftSlopeRange, '.', markersize=2, color=col)
      ax.plot(PlateauDomain, PlateauRange, '.', markersize=2, color=col)
      ax.plot(RightSlopeDomain, RightSlopeRange, '.', markersize=2, color=col)

      # Now plot actual, truncated membership functions
      LeftSlopeDomain = np.linspace(self.LeftFoot[0], self.LeftFoot[0] + ((self.LeftShoulder[0] - self.LeftFoot[0]) * self.Membership), PointsPerSegment)
      LeftSlopeRange = np.linspace(0, self.Membership, PointsPerSegment)
      PlateauDomain = np.linspace(self.LeftFoot[0] + ((self.LeftShoulder[0] - self.LeftFoot[0]) * self.Membership), self.RightShoulder[0] + ((self.RightFoot[0] - self.RightShoulder[0]) * (1.0-self.Membership)), PointsPerSegment)
      PlateauRange = np.ones(PointsPerSegment) * self.Membership
      RightSlopeDomain = np.linspace(self.RightShoulder[0] + ((self.RightFoot[0] - self.RightShoulder[0]) * (1.0-self.Membership)), self.RightFoot[0], PointsPerSegment)
      RightSlopeRange = np.linspace(self.Membership, 0, PointsPerSegment)
      
      ax.plot(LeftSlopeDomain, LeftSlopeRange, '-', color = col, linewidth = 3)
      ax.plot(PlateauDomain, PlateauRange, '-', color = col, linewidth = 3)
      ax.plot(RightSlopeDomain, RightSlopeRange, '-', color = col, linewidth = 3)
      
      return ax
      #plt.show()
        
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
      
  def FuzzyImplication(self, AntecedantMembership, ConsequentMembership=1.0, Method=None):
    if Method == "KD":
      return max(1 - AntecedantMembership, ConsequentMembership)
    else:
      print("Error - Unknown FuzzyImplication method")
      return
        
  def ImplicationAntecedant2Consequent(self, AntecedantMembership, ImplicationTruth=1.0, Method=None):
    # Returns membership of consequent for rule evaluation from AntecedantMembership and the truth of the rule, ImplicationTruth
    if Method == "KD":
      if AntecedantMembership == 0:
        return 0.00001    # Cannot be 0
      else:
        # As true as we must make whichever motor output, given the antecedant
        return AntecedantMembership
    else:
      print("Error - Unknown FuzzyImplication method")
      return


    
class BalanceBot():
  def __init__(self, BM, BMF, RL, RM, MWS):
    self.FL = FuzzyLogic()
    self.OutputDir = './/Output//'
    self.ArenaSeq = 'ArenaSeq//'
    self.FunctionsSeq = 'FunctionsSeq//'
    self.TiltErrorSeq = 'TiltErrorSeq//'
    self.WindSeq = 'WindSeq//'
    self.MotorResponseSeq = 'MotorResponseSeq//'
    
    self.Gravity = 9.81
    self.Time = 0       # Start time, may be used to plot robot responses
    self.dt = 0.25      # Time increment (sec)
    self.RodDragCoefficient = 10    # Force (per rod length - wind speed) in N
    self.MaxWindSpeed = MWS
    
    self.TimeHistory = [self.Time]
    
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
    
    self.ForceHistory = [self.MotorForce]
    self.PositionHistory = [self.Position]
    self.VelocityHistory = [self.Velocity]
    self.AccelerationHistory = [self.Acceleration]
    
    self.Tilt = (np.random.uniform() - 0.5) * 40      # Rod starts upright (deg)
    self.AngularVelocity = (np.random.uniform() - 0.5) * 30            # Start with some initial angular velocity to necessitate adjustment
    self.AngularAcceleration = 0
    
    self.TiltHistory = [self.Tilt]
    self.AngularVelocityHistory = [self.AngularVelocity]
    self.AngularAccelerationHistory = [self.AngularAcceleration]
    
    self.WindSpeed = (np.random.uniform() - 0.5) * 2                 # Will exert external force on robot and rod
    
    self.WindSpeedHistory = [self.WindSpeed]
    self.RelativeWindHistory = [self.WindSpeed - self.Velocity]
    
    # Properties for plotting bot
    self.BotSize = 0.1            # Bot size (width and height, square bot) in meters for plotting
    
    # Fuzzy sets
    self.PosTiltErrorLarge = self.FL.Trapezoid((20,0), (40,1), (90,1), (90,0))
    self.PosTiltErrorMed = self.FL.Trapezoid((0,0), (20,1), (20,1), (40,0))
    self.PosTiltErrorSmall = self.FL.Trapezoid((0,0), (0,1), (0,1), (20,0))

    self.PosWindHigh = self.FL.Trapezoid((0.5 * self.MaxWindSpeed,0), (self.MaxWindSpeed,1), (self.MaxWindSpeed,1), (self.MaxWindSpeed,0))            
    self.PosWindMed = self.FL.Trapezoid((0,0), (0.5 * self.MaxWindSpeed,1), (0.5 * self.MaxWindSpeed,1), (1 * self.MaxWindSpeed,0))                   # Wind speed into direction of tilt; helping wind is always Low
    self.PosWindLow = self.FL.Trapezoid((0,0), (0,1), (0,1), (0.5 * self.MaxWindSpeed,0))                 
    
    self.PosMotorResponseLow = self.FL.Trapezoid((-0.25*self.BotMaxForce,0), (0,1), (0,1), (0.25*self.BotMaxForce,0))
    self.PosMotorResponseMedLow = self.FL.Trapezoid((0,0), (0.25*self.BotMaxForce,1), (0.25*self.BotMaxForce,1), (0.5*self.BotMaxForce,0))
    self.PosMotorResponseMed = self.FL.Trapezoid((0.25*self.BotMaxForce,0), (0.5*self.BotMaxForce,1), (0.5*self.BotMaxForce,1), (0.75*self.BotMaxForce,0))
    self.PosMotorResponseMedHigh = self.FL.Trapezoid((0.5*self.BotMaxForce,0), (0.75*self.BotMaxForce,1), (0.75*self.BotMaxForce,1), (1*self.BotMaxForce,0))
    self.PosMotorResponseHigh = self.FL.Trapezoid((0.75*self.BotMaxForce, 0), (1*self.BotMaxForce,1), (1*self.BotMaxForce, 1), (1*self.BotMaxForce,0))

    self.NegTiltErrorLarge = self.FL.Trapezoid((-90, 0), (-90,1), (-40, 1), (-20,0))
    self.NegTiltErrorMed = self.FL.Trapezoid((-40,0), (-20,1), (-20,1), (0,0))
    self.NegTiltErrorSmall = self.FL.Trapezoid((-20,0), (0,1), (0,1), (0, 0))
    
    self.NegWindHigh = self.FL.Trapezoid((-1 * self.MaxWindSpeed, 0), (-1 * self.MaxWindSpeed, 1), (-1 * self.MaxWindSpeed, 1), (-0.5 * self.MaxWindSpeed, 0))            
    self.NegWindMed = self.FL.Trapezoid( (-1 * self.MaxWindSpeed,0), (-0.5 * self.MaxWindSpeed,1), (-0.5 * self.MaxWindSpeed,1), (0,0))      
    self.NegWindLow = self.FL.Trapezoid((-0.5 * self.MaxWindSpeed,0), (0, 1), (0,1), (0, 0))    
    
    self.NegMotorResponseLow = self.FL.Trapezoid((-0.25*self.BotMaxForce,0), (0,1), (0,1), (0.25*self.BotMaxForce,0))
    self.NegMotorResponseMedLow = self.FL.Trapezoid((-0.5*self.BotMaxForce,0), (-0.25*self.BotMaxForce,1), (-0.25*self.BotMaxForce,1), (0,0))
    self.NegMotorResponseMed = self.FL.Trapezoid((-0.75*self.BotMaxForce,0), (-0.5*self.BotMaxForce,1), (-0.5*self.BotMaxForce,1), (-0.25*self.BotMaxForce,0))
    self.NegMotorResponseMedHigh = self.FL.Trapezoid((-1*self.BotMaxForce,0), (-0.75*self.BotMaxForce,1), (-0.75*self.BotMaxForce,1), (-0.5*self.BotMaxForce,0))
    self.NegMotorResponseHigh = self.FL.Trapezoid((-1*self.BotMaxForce, 0), (-1*self.BotMaxForce, 1), (-1*self.BotMaxForce, 1), (-0.75*self.BotMaxForce, 0))
       
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
    plt.axis([-5, 5, 0, 1])
    plt.savefig(self.OutputDir + self.ArenaSeq + FileName)
    ax.clear()
    
  def PlotFuzzySetsToFile(self, OutputFiles=[], FuzzySets=[]):   # FuzzySets is list of strings indicating which rule groups to plot (eg. 'TiltError', 'Wind', 'MotorResponse')
    # Assumes each element of FuzzySets is homogeneous wrt units (they can be plotted on the same axes)
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines
    PointsPerSegment = 50
    if 'TiltError' in FuzzySets:
      ax = plt.axes()
      # PosTiltErrorLarge
      ax = self.PosTiltErrorLarge.PrintMembershipFunctionToAxes('r', ax)
      RedSolid = mlines.Line2D([], [], color='r', label='+TEL', lineStyle='-')
      
      # PosTiltErrorMed
      ax = self.PosTiltErrorMed.PrintMembershipFunctionToAxes('b', ax)
      BlueSolid = mlines.Line2D([], [], color='b', label='+TEM', lineStyle='-')
      
      # PosTiltErrorSmall
      ax = self.PosTiltErrorSmall.PrintMembershipFunctionToAxes('y', ax)
      YellowSolid = mlines.Line2D([], [], color='y', label='+TES', lineStyle='-')

      # NegTiltErrorLarge
      ax = self.NegTiltErrorLarge.PrintMembershipFunctionToAxes('g', ax)
      GreenSolid = mlines.Line2D([], [], color='g', label='-TEL', lineStyle='-')

      # NegTiltErrorMed
      ax = self.NegTiltErrorMed.PrintMembershipFunctionToAxes('orange', ax)
      OrangeSolid = mlines.Line2D([], [], color='orange', label='-TEM', lineStyle='-')

      # NegTiltErrorSmall
      ax = self.NegTiltErrorSmall.PrintMembershipFunctionToAxes('purple', ax)
      PurpleSolid = mlines.Line2D([], [], color='purple', label='-TES', lineStyle='-')
      
      plt.title('TiltError')
      ax.set_xlabel('Rod tilt error (deg)')
      ax.set_ylabel('Membership')
      
      ax.plot(self.PosTiltErrorLarge.CrispValue*np.ones(PointsPerSegment), np.linspace(0,1,PointsPerSegment), '|', color='k', linewidth=32)
      ax.text(self.PosTiltErrorLarge.RightFoot[0]*0.75, 1.1, 'CV=' + str(self.PosTiltErrorLarge.CrispValue), size=16)
      
      plt.legend(handles=[RedSolid, BlueSolid, YellowSolid, GreenSolid, OrangeSolid, PurpleSolid])
      plt.savefig(self.OutputDir + self.FunctionsSeq + self.TiltErrorSeq + OutputFiles[FuzzySets.index('TiltError')])
      ax.clear()
      
    if 'Wind' in FuzzySets:
      ax = plt.axes()
      # PosWindHigh
      ax = self.PosWindHigh.PrintMembershipFunctionToAxes('r', ax)
      RedSolid = mlines.Line2D([], [], color='r', label='+WH', lineStyle='-')
      
      # PosWindMed
      ax = self.PosWindMed.PrintMembershipFunctionToAxes('b', ax)
      BlueSolid = mlines.Line2D([], [], color='b', label='+WM', lineStyle='-')
      
      # PosWindLow
      ax = self.PosWindLow.PrintMembershipFunctionToAxes('y', ax)
      YellowSolid = mlines.Line2D([], [], color='y', label='+WL', lineStyle='-')
      
      # NegWindHigh
      ax = self.NegWindHigh.PrintMembershipFunctionToAxes('g', ax)
      GreenSolid = mlines.Line2D([], [], color='g', label='-WH', lineStyle='-')    
      
      # NegWindMed
      ax = self.NegWindMed.PrintMembershipFunctionToAxes('orange', ax)
      OrangeSolid = mlines.Line2D([], [], color='orange', label='-WM', lineStyle='-')
      
      # NegWindLow
      ax = self.NegWindLow.PrintMembershipFunctionToAxes('purple', ax)
      PurpleSolid = mlines.Line2D([], [], color='purple', label='-WL', lineStyle='-')
    
      plt.title('Wind')
      ax.set_xlabel('Wind speed')
      ax.set_ylabel('Membership')
      
      ax.plot(self.PosWindHigh.CrispValue*np.ones(PointsPerSegment), np.linspace(0,1,PointsPerSegment), '|', color='k', linewidth=32)
      ax.text(self.PosWindHigh.RightFoot[0]*0.75, 1.1, 'CV=' + str(self.PosWindHigh.CrispValue), size=16)
      
      plt.legend(handles=[RedSolid, BlueSolid, YellowSolid, GreenSolid, OrangeSolid, PurpleSolid])
      plt.savefig(self.OutputDir + self.FunctionsSeq + self.WindSeq + OutputFiles[FuzzySets.index('Wind')])
      ax.clear()
      
    if 'MotorResponse' in FuzzySets:
      ax = plt.axes()
      
      # PosMotorResponseHigh
      ax = self.PosMotorResponseHigh.PrintMembershipFunctionToAxes('r', ax)
      RedSolid = mlines.Line2D([], [], color='r', label='+MRH', lineStyle='-')
      
      # PosMotorResponseMedHigh
      ax = self.PosMotorResponseMedHigh.PrintMembershipFunctionToAxes('b', ax)
      BlueSolid = mlines.Line2D([], [], color='b', label='+MRmH', lineStyle='-')

      # PosMotorResponseMed
      ax = self.PosMotorResponseMed.PrintMembershipFunctionToAxes('y', ax)
      YellowSolid = mlines.Line2D([], [], color='y', label='+MRM', lineStyle='-')

      # PosMotorResponseMedLow
      ax = self.PosMotorResponseMedLow.PrintMembershipFunctionToAxes('c', ax)
      CyanSolid = mlines.Line2D([], [], color='c', label='+MRmL', lineStyle='-')

      # PosMotorResponseLow
      ax = self.PosMotorResponseLow.PrintMembershipFunctionToAxes('m', ax)
      MagentaSolid = mlines.Line2D([], [], color='m', label='+MRL', lineStyle='-')
      
      # NegMotorResponseHigh
      ax = self.NegMotorResponseHigh.PrintMembershipFunctionToAxes('g', ax)
      GreenSolid = mlines.Line2D([], [], color='g', label='-MRH', lineStyle='-')
      
      # NegMotorResponseMedHigh
      ax = self.NegMotorResponseMedHigh.PrintMembershipFunctionToAxes('orange', ax)
      OrangeSolid = mlines.Line2D([], [], color='orange', label='-MRmH', lineStyle='-')

      # NegMotorResponseMed
      ax = self.NegMotorResponseMed.PrintMembershipFunctionToAxes('purple', ax)
      PurpleSolid = mlines.Line2D([], [], color='purple', label='-MRM', lineStyle='-')

      # NegMotorResponseMedLow
      ax = self.NegMotorResponseMedLow.PrintMembershipFunctionToAxes('pink', ax)
      PinkSolid = mlines.Line2D([], [], color='pink', label='-MRmL', lineStyle='-')

      # NegMotorResponseLow
      ax = self.NegMotorResponseLow.PrintMembershipFunctionToAxes('brown', ax)
      BrownSolid = mlines.Line2D([], [], color='brown', label='-MRL', lineStyle='-')
      
      plt.title('MotorResponse')
      ax.set_xlabel('Motor force (N)')
      ax.set_ylabel('Membership')
      
      ax.plot(self.MotorForce*np.ones(PointsPerSegment), np.linspace(0,1,PointsPerSegment), '|', color='k', linewidth=32)
      ax.text(self.PosMotorResponseHigh.RightFoot[0]*0.75, 1.1, 'CV=' + str(self.MotorForce), size=16)
      
      plt.legend(handles=[RedSolid, BlueSolid, YellowSolid, CyanSolid, MagentaSolid, BrownSolid, PinkSolid, PurpleSolid, OrangeSolid, GreenSolid])
      plt.savefig(self.OutputDir + self.FunctionsSeq + self.MotorResponseSeq + OutputFiles[FuzzySets.index('MotorResponse')])
      ax.clear()
      
  def PlotQuantityHistories(self, Quantities=[]):    # Quantities is list of strings ['Position','Acceleration']
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines
    fig = plt.figure()
    
    if 'Position' in Quantities:
      ax1 = fig.add_subplot(411)
      ax1.plot(self.TimeHistory, self.PositionHistory, 'r')
      ax1.set_xlabel('Time (s)')
      ax1.set_ylabel('Position (m)')
    PositionLine = mlines.Line2D(self.PositionHistory, self.TimeHistory, color='r', label='Position', lineStyle='-')
    
    if 'Velocity' in Quantities:
      ax2 = fig.add_subplot(412)
      ax2.plot(self.TimeHistory, self.VelocityHistory, 'b')
      ax2.set_xlabel('Time (s)')
      ax2.set_ylabel('Velocity (m/s)')
    VelocityLine = mlines.Line2D(self.VelocityHistory, self.TimeHistory, color='b', label='Velocity', lineStyle='-')
    
    if 'Acceleration' in Quantities:
      ax3 = fig.add_subplot(413)
      ax3.plot(self.TimeHistory, self.AccelerationHistory, 'orange')
      ax3.set_xlabel('Time (s)')
      ax3.set_ylabel('Acceleration (m/s2)')
    AccelerationLine = mlines.Line2D(self.AccelerationHistory, self.TimeHistory, color='orange', label='Acceleration', lineStyle='-')
    
    if 'Tilt' in Quantities:
      ax4 = fig.add_subplot(414)
      ax4.plot(self.TimeHistory, self.TiltHistory, 'purple')
      ax4.set_xlabel('Time (s)')
      ax4.set_ylabel('Tilt (deg)')
    TiltLine = mlines.Line2D(self.TiltHistory, self.TimeHistory, color='purple', label='Tilt', lineStyle='-')
    
    plt.legend(handles=[PositionLine, VelocityLine, AccelerationLine, TiltLine])
    
    #if 'Tilt'  in Quantities:
      #plt.plot(self.TimeHistory, self.TiltHistory)
    plt.show()
    
  def UpdateFuzzySets(self):
    #RelativeWind = self.WindSpeed - self.Velocity
    ImplicationMethod = 'KD'
    tNorm = 'min'
    sNorm = 'max'
    
    # ------- Positive direction sets - CW rotations, right-wards translation ------- #
    self.PosTiltErrorLarge.ComputeMembership(self.Tilt)
    self.PosTiltErrorMed.ComputeMembership(self.Tilt)
    self.PosTiltErrorSmall.ComputeMembership(self.Tilt)
    
    self.PosWindHigh.ComputeMembership(self.WindSpeed)
    self.PosWindMed.ComputeMembership(self.WindSpeed)
    self.PosWindLow.ComputeMembership(self.WindSpeed)
    
    # (Re)initialize MotorResponseRules
    PosOutputLowRules = [0, 0, 0]
    PosOutputMedLowRules = [0]
    PosOutputMedRules = [0, 0, 0]
    PosOutputMedHighRules = [0, 0]
    PosOutputHighRules = [0, 0, 0]
    
    # TiltErrorSmall --> MotorResponseMagnitudeLow
    PosOutputLowRules[0] = self.FL.ImplicationAntecedant2Consequent(self.PosTiltErrorSmall.Membership, 1, ImplicationMethod)
    
    # TiltErrorSmall and WindLow --> MotorResponseMagnitudeLow
    PosOutputLowRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorSmall and WindMed --> MotorResponseMagnitudeLow
    PosOutputLowRules[2] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseLow.Membership = self.FL.FuzzyDisjunction(PosOutputLowRules, sNorm)
    
    # TiltErrorSmall and WindHigh --> MotorResponseMagnitudeMedLow
    PosOutputMedLowRules[0] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(PosOutputMedLowRules, sNorm)
    
    # TiltErrorMed --> MotorResponseMagnitudeMed
    PosOutputMedRules[0] = self.FL.ImplicationAntecedant2Consequent(self.PosTiltErrorMed.Membership, 1, ImplicationMethod)
    
    # TiltErrorMed and WindLow --> MotorResponseMagnitudeMed
    PosOutputMedRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorMed and WindMed --> MotorResponseMagnitudeMed
    PosOutputMedRules[2] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMed.Membership = self.FL.FuzzyDisjunction(PosOutputMedRules, sNorm)
    
    # TiltErrorMed and WindHigh --> MotorResponseMagnitudeMedHigh
    PosOutputMedHighRules[0] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindLow --> MotorResponseMagnitudeMedHigh
    PosOutputMedHighRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    self.PosMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(PosOutputMedHighRules, sNorm)
    
    # TiltErrorLarge --> MotorResponseMagnitudeHigh
    PosOutputHighRules[0] = self.FL.ImplicationAntecedant2Consequent(self.PosTiltErrorLarge.Membership, 1, ImplicationMethod)
    
    # TiltErrorLarge and WindMed --> MotorResponseMagnitudeHigh
    PosOutputHighRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    PosOutputHighRules[2] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
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
    
    self.NegWindHigh.ComputeMembership(self.WindSpeed)
    self.NegWindMed.ComputeMembership(self.WindSpeed)
    self.NegWindLow.ComputeMembership(self.WindSpeed)
    
    # (Re)initialize MotorResponseRules
    NegOutputLowRules = [0, 0, 0]
    NegOutputMedLowRules = [0]
    NegOutputMedRules = [0, 0, 0]
    NegOutputMedHighRules = [0, 0]
    NegOutputHighRules = [0, 0, 0]
    
    # TiltErrorSmall --> MotorResponseMagnitudeLow
    NegOutputLowRules[0] = self.FL.ImplicationAntecedant2Consequent(self.NegTiltErrorSmall.Membership, 1, ImplicationMethod)
    
    # TiltErrorSmall and WindLow --> MotorResponseMagnitudeLow
    NegOutputLowRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorSmall and WindMed --> MotorResponseMagnitudeLow
    NegOutputLowRules[2] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.NegMotorResponseLow.Membership = self.FL.FuzzyDisjunction(NegOutputLowRules, sNorm)
    
    # TiltErrorSmall and WindHigh --> MotorResponseMagnitudeMedLow
    NegOutputMedLowRules[0] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    self.NegMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(NegOutputMedLowRules, sNorm)
    
    # TiltErrorMed --> MotorResponseMagnitudeMed
    NegOutputMedRules[0] = self.FL.ImplicationAntecedant2Consequent(self.NegTiltErrorMed.Membership, 1, ImplicationMethod)
    
    # TiltErrorMed and WindLow --> MotorResponseMagnitudeMed
    NegOutputMedRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorMed and WindMed --> MotorResponseMagnitudeMed
    NegOutputMedRules[2] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    self.NegMotorResponseMed.Membership = self.FL.FuzzyDisjunction(NegOutputMedRules, sNorm)
    
    # TiltErrorMed and WindHigh --> MotorResponseMagnitudeMedHigh
    NegOutputMedHighRules[0] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindLow --> MotorResponseMagnitudeMedHigh
    NegOutputMedHighRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod)
    
    self.NegMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(NegOutputMedHighRules, sNorm)
    
    # TiltErrorSmall --> MotorResponseMagnitudeHigh
    NegOutputHighRules[0] = self.FL.ImplicationAntecedant2Consequent(self.NegTiltErrorLarge.Membership, 1, ImplicationMethod)
    
    # TiltErrorLarge and WindMed --> MotorResponseMagnitudeHigh
    NegOutputHighRules[1] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod)
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    NegOutputHighRules[2] = self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod)
    
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
      self.MotorForce = ((self.NegMotorResponseLow.Area * self.NegMotorResponseLow.COA) + (self.NegMotorResponseMedLow.Area * self.NegMotorResponseMedLow.COA) + (self.NegMotorResponseMed.Area * self.NegMotorResponseMed.COA) + (self.NegMotorResponseMedHigh.Area * self.NegMotorResponseMedHigh.COA) + (self.NegMotorResponseHigh.Area * self.NegMotorResponseHigh.COA)) / (TotalSetMass)
      
    else:   # Move in positive direction
      TotalSetMass = self.PosMotorResponseLow.Area + self.PosMotorResponseMedLow.Area + self.PosMotorResponseMed.Area + self.PosMotorResponseMedHigh.Area + self.PosMotorResponseHigh.Area
      self.MotorForce = ((self.PosMotorResponseLow.Area * self.PosMotorResponseLow.COA) + (self.PosMotorResponseMedLow.Area * self.PosMotorResponseMedLow.COA) + (self.PosMotorResponseMed.Area * self.PosMotorResponseMed.COA) + (self.PosMotorResponseMedHigh.Area * self.PosMotorResponseMedHigh.COA) + (self.PosMotorResponseHigh.Area * self.PosMotorResponseHigh.COA)) / (TotalSetMass)
  
  def UpdateMechanicalState(self):
    self.Time += self.dt
    self.TimeHistory.append(self.Time)
    
    #RelativeWind = self.WindSpeed - self.Velocity
    
    self.Acceleration = self.MotorForce / self.BotMass
    self.Position += 0.5 * (self.Acceleration) * (self.dt ** 2)
    self.Velocity += self.Acceleration * self.dt
    
    self.AccelerationHistory.append(self.Acceleration)
    self.PositionHistory.append(self.Position)
    self.VelocityHistory.append(self.Velocity)
    
    # Start with BalanceRod - experiences torques from gravity, bot acceleration, and wind
    GravitationalTorque = self.Gravity * self.RodMass * np.sin(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    AccelerationTorque = -1*self.Acceleration * self.RodMass * np.sin(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    WindTorque = self.WindSpeed * self.RodLength * np.sin(self.Tilt * np.pi / 180.0) * self.RodDragCoefficient * (self.RodLength/2.0)
    RodTorque = GravitationalTorque + AccelerationTorque + WindTorque
    print ("GravitationalTorque", "AccelerationTorque", "WindTorque", "TotalTorque")
    print (GravitationalTorque, AccelerationTorque, WindTorque, RodTorque)
    
    #print(GravitationalTorque, AccelerationTorque)
    self.AngularAcceleration = RodTorque / self.RodMomentOfInertia
    self.Tilt += 0.5 * self.AngularAcceleration * (self.dt ** 2)
    self.AngularVelocity += self.AngularAcceleration * self.dt
    
    self.AngularAccelerationHistory.append(self.AngularAcceleration)
    self.TiltHistory.append(self.Tilt)
    self.AngularVelocityHistory.append(self.AngularVelocity)
    
  def StartBalancing(self):
    self.UpdateMechanicalState()
    self.UpdateFuzzySets()
    self.UpdateControls()
    
Bot = BalanceBot(10, 100, 0.25, 10, 10)
#Bot.StartBalancing()
#Bot.PosTiltErrorLarge.PrintMembershipFunction('.\\', 'Membership.png')


for TestIt in range(100):
  Bot.StartBalancing()
  #Bot.DrawBotToFile('arena' + str(TestIt) + '.png')
  #Bot.PlotFuzzySetsToFile(['TiltError' + str(TestIt) + '.png', 'RelativeWind' + str(TestIt) + '.png', 'MotorResponse' + str(TestIt) + '.png'], ['TiltError', 'Wind', 'MotorResponse'])
Bot.PlotQuantityHistories(['Position', 'Velocity', 'Acceleration', 'Tilt'])