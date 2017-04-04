import csv, math
import numpy as np
import matplotlib as mpl
from FuzzyLogic import FuzzyLogic

class BalanceBot():
  def __init__(self, BM, BMF, RL, RM, MWS):
    self.FL = FuzzyLogic()
    self.OutputDir = './/Output//'
    self.ArenaSeq = 'ArenaSeq//'
    self.FunctionsSeq = 'FunctionsSeq//'
    self.TiltErrorSeq = 'TiltErrorSeq//'
    self.TiltIntegralSeq = 'TiltIntegralSeq//'
    self.WindSeq = 'WindSeq//'
    self.MotorResponseSeq = 'MotorResponseSeq//'
    
    # Environment physical quantities 
    self.Gravity = 9.81
    self.Time = 0       # Start time, may be used to plot robot responses
    self.dt = 0.1      # Time increment (sec)
    self.RodDragCoefficient = 10    # Force (per rod length - wind speed) in N
    self.MaxWindSpeed = MWS
    
    self.TimeHistory = [self.Time]
    
    # Robot physical quantities
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
    
    # Initial values of 0 may not be absolutely correct, but needed for plotting dimension agreement
    self.GravitationalTorqueHistory = [0]
    self.AccelerationTorqueHistory = [0]
    self.WindTorqueHistory = [0]
    self.TotalTorqueHistory = [0]
    
    self.Tilt = (np.random.uniform() - 0.5) * 40      # Rod starts upright (deg)
    self.AngularVelocity = (np.random.uniform() - 0.5) * 30            # Start with some initial angular velocity to necessitate adjustment
    self.AngularAcceleration = 0
    
    self.TiltHistory = [self.Tilt]
    self.AngularVelocityHistory = [self.AngularVelocity]
    self.AngularAccelerationHistory = [self.AngularAcceleration]
    
    self.WindSpeed = (np.random.uniform() - 0.5) * 2                 # Will exert external force on robot and rod
    
    self.WindSpeedHistory = [self.WindSpeed]
    self.RelativeWindHistory = [self.WindSpeed - self.Velocity]
    
    # Integrals
    self.TiltIntegral = self.Tilt * self.dt
    
    # Properties for plotting bot
    self.BotSize = 0.1            # Bot size (width and height, square bot) in meters for plotting
    
    # Fuzzy sets
    self.PosTiltErrorLarge = self.FL.Trapezoid((20,0), (40,1), (90,1), (90,0))
    self.PosTiltErrorMed = self.FL.Trapezoid((0,0), (20,1), (20,1), (40,0))
    self.PosTiltErrorSmall = self.FL.Trapezoid((0,0), (0,1), (0,1), (20,0))

    self.PosWindHigh = self.FL.Trapezoid((0.5 * self.MaxWindSpeed,0), (self.MaxWindSpeed,1), (self.MaxWindSpeed,1), (self.MaxWindSpeed,0))            
    self.PosWindMed = self.FL.Trapezoid((0,0), (0.5 * self.MaxWindSpeed,1), (0.5 * self.MaxWindSpeed,1), (1 * self.MaxWindSpeed,0))                   # Wind speed into direction of tilt; helping wind is always Low
    self.PosWindLow = self.FL.Trapezoid((0,0), (0,1), (0,1), (0.5 * self.MaxWindSpeed,0))                 
    
    # Use integral control to get rod to flip past 0 deg?
    self.PosTiltIntegralHigh = self.FL.Trapezoid((10,0), (20,1), (1000,1), (1000,0))
    self.PosTiltIntegralMed = self.FL.Trapezoid((0,0), (10,1), (10,1), (20,0))
    self.PosTiltIntegralLow = self.FL.Trapezoid((0,0), (0,1), (0,1), (10,0))
    
    self.PosMotorResponseLow = self.FL.Trapezoid((0,0), (0,1), (0,1), (0.25*self.BotMaxForce,0))
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
    
    self.NegTiltIntegralHigh = self.FL.Trapezoid((-1000,0), (-1000,1), (-20,1), (-10,0))
    self.NegTiltIntegralMed = self.FL.Trapezoid((-20,0), (-10,1), (-10,1), (0,0))
    self.NegTiltIntegralLow = self.FL.Trapezoid((-10,0), (0,1), (0,1), (0,0))
    
    self.NegMotorResponseLow = self.FL.Trapezoid((-0.25*self.BotMaxForce,0), (0,1), (0,1), (0,0))
    self.NegMotorResponseMedLow = self.FL.Trapezoid((-0.5*self.BotMaxForce,0), (-0.25*self.BotMaxForce,1), (-0.25*self.BotMaxForce,1), (0,0))
    self.NegMotorResponseMed = self.FL.Trapezoid((-0.75*self.BotMaxForce,0), (-0.5*self.BotMaxForce,1), (-0.5*self.BotMaxForce,1), (-0.25*self.BotMaxForce,0))
    self.NegMotorResponseMedHigh = self.FL.Trapezoid((-1*self.BotMaxForce,0), (-0.75*self.BotMaxForce,1), (-0.75*self.BotMaxForce,1), (-0.5*self.BotMaxForce,0))
    self.NegMotorResponseHigh = self.FL.Trapezoid((-1*self.BotMaxForce, 0), (-1*self.BotMaxForce, 1), (-1*self.BotMaxForce, 1), (-0.75*self.BotMaxForce, 0))
       
  def DrawBotToFile(self, FileName, ReferenceFrame):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    ax = plt.axes()
    
    # Draw bot body as patch, and balance rod as arrow
    BotPatch = patches.Rectangle((self.Position - (self.BotSize / 2.0), 0), self.BotSize, self.BotSize, linewidth = 1, edgecolor = 'k', facecolor = 'k')
    ax.add_patch(BotPatch)
    ax.arrow(self.Position, self.BotSize, self.RodLength * np.sin((self.Tilt) * np.pi / 180.0), self.RodLength * np.cos((self.Tilt) * np.pi / 180.0), linewidth = 3, head_width = 0.05, head_length=0.05, fc='k')
    
    if ReferenceFrame == "Ground":
      # Annotate with wind speed arrow
      ax.arrow(0.5, 0.9, self.WindSpeed / 2.0, 0, linewidth = 3, head_width = 0.05, head_length=0.05, ec = 'g', fc='g')
      ax.text(0.4, 0.95, 'Wind Speed: ' + str(self.WindSpeed)[:5], color='g')
      
      # Annotate with currrent time
      ax.text(-4.5, 0.95, 'Time: ' + str(self.Time), color='b')
      
      ax.text(-4.5, 0.85, 'Tilt (deg): ' + str(self.Tilt), color='r')
      
      plt.axis([-5, 5, 0, 1])
    elif ReferenceFrame == "Bot":
      # Annotate with wind speed arrow
      ax.arrow(self.Position + 0.5, 0.9, self.WindSpeed / 2.0, 0, linewidth = 3, head_width = 0.05, head_length=0.05, ec = 'g', fc='g')
      ax.text(self.Position + 0.4, 0.95, 'Wind Speed: ' + str(self.WindSpeed)[:5], color='g')
      
      # Annotate with currrent time
      ax.text(self.Position - 0.5, 0.95, 'Time: ' + str(self.Time), color='b')
      
      ax.text(self.Position - 0.5, 0.85, 'Tilt (deg): ' + str(self.Tilt), color='r')
      
      plt.axis([self.Position - 1, self.Position + 1, 0, 1])
      
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
      
      ax.axvline(self.PosTiltErrorLarge.CrispValue, color='k', linewidth=3)
      ax.text(self.PosTiltErrorLarge.RightFoot[0]*0.75, 1.1, 'CV=' + str(self.PosTiltErrorLarge.CrispValue), size=16)
      
      plt.legend(handles=[RedSolid, BlueSolid, YellowSolid, GreenSolid, OrangeSolid, PurpleSolid])
      plt.savefig(self.OutputDir + self.FunctionsSeq + self.TiltErrorSeq + OutputFiles[FuzzySets.index('TiltError')])
      ax.clear()
      
    if 'TiltIntegral' in FuzzySets:
      ax = plt.axes()
      
      # PosTiltIntegralHigh
      ax = self.PosTiltIntegralHigh.PrintMembershipFunctionToAxes('r', ax)
      PosTiltIntegralHighLine = mlines.Line2D([], [], color='r', label='+TIH', lineStyle='-')
      
      # PosTiltIntegralMed
      ax = self.PosTiltIntegralMed.PrintMembershipFunctionToAxes('b', ax)
      PosTiltIntegralMedLine = mlines.Line2D([], [], color='b', label='+TIM', lineStyle='-')
      
      # PosTiltIntegralLow
      ax = self.PosTiltIntegralLow.PrintMembershipFunctionToAxes('y', ax)
      PosTiltIntegralLow = mlines.Line2D([], [], color='y', label='+TIL', lineStyle='-')
      
      # NegTiltIntegralHigh
      ax = self.NegTiltIntegralHigh.PrintMembershipFunctionToAxes('g', ax)
      NegTiltIntegralHighLine = mlines.Line2D([], [], color='g', label='-TIH', lineStyle='-')
      
      # NegTiltIntegralMed
      ax = self.NegTiltIntegralMed.PrintMembershipFunctionToAxes('orange', ax)
      NegTiltIntegralMedLine = mlines.Line2D([], [], color='orange', label='-TIM', lineStyle='-')
      
      # NegTiltIntegralLow
      ax = self.NegTiltIntegralLow.PrintMembershipFunctionToAxes('purple', ax)
      NegTiltIntegralLow = mlines.Line2D([], [], color='purple', label='-TIL', lineStyle='-')
      
      plt.title('TiltIntegral')
      ax.set_xlabel('Tilt integral')
      ax.set_ylabel('Membership')
      ax.set_autoscalex_on(False)
      ax.set_xbound(lower=-30, upper=30)
      
      ax.axvline(x=self.PosTiltIntegralHigh.CrispValue, color='k', linewidth=3)
      ax.text(self.PosTiltIntegralHigh.LeftShoulder[0]*0.75, 1.1, 'CV=' + str(self.PosTiltIntegralHigh.CrispValue), size=16)
      
      plt.legend(handles=[PosTiltIntegralHighLine, PosTiltIntegralMedLine, PosTiltIntegralLow, NegTiltIntegralHighLine, NegTiltIntegralMedLine, NegTiltIntegralLow])
      plt.savefig(self.OutputDir + self.FunctionsSeq + self.TiltIntegralSeq + OutputFiles[FuzzySets.index('TiltIntegral')])
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

      ax.axvline(self.PosWindHigh.CrispValue, color='k', linewidth=3)
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
      
      ax.axvline(x=self.MotorForce, color='k', linewidth=3)
      ax.text(self.PosMotorResponseHigh.RightFoot[0]*0.75, 1.1, 'CV=' + str(self.MotorForce), size=16)
      
      plt.legend(handles=[RedSolid, BlueSolid, YellowSolid, CyanSolid, MagentaSolid, BrownSolid, PinkSolid, PurpleSolid, OrangeSolid, GreenSolid])
      plt.savefig(self.OutputDir + self.FunctionsSeq + self.MotorResponseSeq + OutputFiles[FuzzySets.index('MotorResponse')])
      ax.clear()
      
  def PlotQuantityHistories(self, Quantities=[]):    # Quantities is list of strings ['Position','Acceleration']
    import matplotlib.pyplot as plt
    import matplotlib.lines as mlines

    fig1name = 'fig1.png'
    fig2name = 'fig2.png'
    
    if 'Kinematics' in Quantities:
      fig1 = plt.figure()

      ax1 = fig1.add_subplot(411)
      ax1.plot(self.TimeHistory, self.PositionHistory, 'r')
      ax1.set_xlabel('Time (s)')
      ax1.set_ylabel('Position (m)')
      PositionLine = mlines.Line2D(self.PositionHistory, self.TimeHistory, color='r', label='Position', lineStyle='-')

      ax2 = fig1.add_subplot(412)
      ax2.plot(self.TimeHistory, self.VelocityHistory, 'b')
      ax2.set_xlabel('Time (s)')
      ax2.set_ylabel('Velocity (m/s)')
      VelocityLine = mlines.Line2D(self.VelocityHistory, self.TimeHistory, color='b', label='Velocity', lineStyle='-')

      ax3 = fig1.add_subplot(413)
      ax3.plot(self.TimeHistory, self.AccelerationHistory, 'orange')
      ax3.set_xlabel('Time (s)')
      ax3.set_ylabel('Acceleration (m/s^2)')
      AccelerationLine = mlines.Line2D(self.AccelerationHistory, self.TimeHistory, color='orange', label='Acceleration', lineStyle='-')

      ax4 = fig1.add_subplot(414)
      ax4.plot(self.TimeHistory, self.TiltHistory, 'purple')
      ax4.set_xlabel('Time (s)')
      ax4.set_ylabel('Tilt (deg)')
      ax4.set_autoscaley_on(False)
      ax4.set_ybound(-100,100)
      TiltLine = mlines.Line2D(self.TiltHistory, self.TimeHistory, color='purple', label='Tilt', lineStyle='-')

      plt.legend(handles=[PositionLine, VelocityLine, AccelerationLine, TiltLine])
      plt.savefig(self.OutputDir + fig1name)
      
      ax1.clear()
      ax2.clear()
      ax3.clear()
      ax4.clear()
      
    fig2 = plt.figure()
    
    if 'AngularDynamics' in Quantities:
      ax5 = fig2.add_subplot(411)
      ax5.plot(self.TimeHistory, self.GravitationalTorqueHistory, 'r')
      ax5.set_xlabel('Time (s)')
      ax5.set_ylabel('GravitationalTorque (N-m)')
      GravitationalTorqueLine = mlines.Line2D(self.GravitationalTorqueHistory, self.TimeHistory, color='r', label='Gravitational', linestyle='-')

      ax6 = fig2.add_subplot(412)
      ax6.plot(self.TimeHistory, self.AccelerationTorqueHistory, color='b')
      ax6.set_xlabel('Time (s)')
      ax6.set_ylabel('AccelerationTorque (N-m)')
      AccelerationTorqueLine = mlines.Line2D(self.AccelerationTorqueHistory, self.TimeHistory, color='b', label='Acceleration', lineStyle='-')
    
      ax7 = fig2.add_subplot(413)
      ax7.plot(self.TimeHistory, self.WindTorqueHistory, color='orange')
      ax7.set_xlabel('Time (s)')
      ax7.set_ylabel('WindTorque (N-m)')
      WindTorqueLine = mlines.Line2D(self.WindTorqueHistory, self.TimeHistory, color='orange', label='Wind', lineStyle='-')

      ax8 = fig2.add_subplot(414)
      ax8.plot(self.TimeHistory, self.TotalTorqueHistory, color='purple')
      ax8.set_xlabel('Time (s)')
      ax8.set_ylabel('TotalTorque (N-m)')
      TotalTorqueLine = mlines.Line2D(self.TotalTorqueHistory, self.TimeHistory, color='purple', label='Total', lineStyle='-')

      plt.legend(handles=[GravitationalTorqueLine, AccelerationTorqueLine, WindTorqueLine, TotalTorqueLine])
      plt.savefig(self.OutputDir + fig2name)
      
      ax5.clear()
      ax6.clear()
      ax7.clear()
      ax8.clear()
    
  def UpdateFuzzySets(self, sNorm, tNorm, ImplicationMethod):
    #RelativeWind = self.WindSpeed - self.Velocity
    
    # ------- Positive direction sets - CW rotations, right-wards translation ------- #
    self.PosTiltErrorLarge.ComputeMembership(self.Tilt)
    self.PosTiltErrorMed.ComputeMembership(self.Tilt)
    self.PosTiltErrorSmall.ComputeMembership(self.Tilt)
    
    self.PosTiltIntegralHigh.ComputeMembership(self.TiltIntegral)
    self.PosTiltIntegralMed.ComputeMembership(self.TiltIntegral)
    self.PosTiltIntegralLow.ComputeMembership(self.TiltIntegral)
    
    self.PosWindHigh.ComputeMembership(self.WindSpeed)
    self.PosWindMed.ComputeMembership(self.WindSpeed)
    self.PosWindLow.ComputeMembership(self.WindSpeed)
    
    # (Re)initialize MotorResponseRules
    PosOutputLowRules = []
    PosOutputMedLowRules = []
    PosOutputMedRules = []
    PosOutputMedHighRules = []
    PosOutputHighRules = []
    
    # PosTiltErrorSmall --> PosMotorResponseLow
    PosOutputLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.PosTiltErrorSmall.Membership, 1, ImplicationMethod))
    
    # PosTiltErrorSmall and PosWindLow --> PosMotorResponseLow
    #PosOutputLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod))
    
    # PosTiltErrorSmall and PosWindMed --> PosMotorResponseLow
    #PosOutputLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod))
    
    self.PosMotorResponseLow.Membership = self.FL.FuzzyDisjunction(PosOutputLowRules, sNorm)
    
    # PosTiltErrorSmall and PosWindHigh --> PosMotorResponseMedLow
    #PosOutputMedLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorSmall.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod))
    
    self.PosMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(PosOutputMedLowRules, sNorm)
    
    # PosTiltErrorMed --> PosMotorResponseMed
    PosOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.PosTiltErrorMed.Membership, 1, ImplicationMethod))
    
    # NegTiltIntegralLow --> PosMotorResponseMed
    PosOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.NegTiltIntegralLow.Membership, 1, ImplicationMethod))
    
    # PosTiltErrorMed and PosWindLow --> PosMotorResponseMed
    #PosOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod))
    
    # PosTiltErrorMed and PosWindMed --> PosMotorResponseMed
    #PosOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod))
    
    self.PosMotorResponseMed.Membership = self.FL.FuzzyDisjunction(PosOutputMedRules, sNorm)
    
    # PosTiltErrorMed and PosWindHigh --> PosMotorResponseMedHigh
    #PosOutputMedHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorMed.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod))
    
    # PosTiltErrorLarge and PosWindLow --> PosMotorResponseMedHigh
    #PosOutputMedHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindLow.Membership], tNorm), 1, ImplicationMethod))
    
    # NegTiltIntegralMed --> PosResponseMedHigh
    PosOutputMedHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.NegTiltIntegralMed.Membership, 1, ImplicationMethod))
    
    self.PosMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(PosOutputMedHighRules, sNorm)
    
    # PosTiltErrorLarge --> PosMotorResponseHigh
    PosOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.PosTiltErrorLarge.Membership, 1, ImplicationMethod))
    
    # NegTiltIntegralHigh --> PosMotorResponseHigh
    PosOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.NegTiltIntegralHigh.Membership, 1, ImplicationMethod))
    
    # PosTiltErrorLarge and PosWindMed --> PosMotorResponseHigh
    #PosOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindMed.Membership], tNorm), 1, ImplicationMethod))
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    #PosOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.PosTiltErrorLarge.Membership, self.PosWindHigh.Membership], tNorm), 1, ImplicationMethod))
    
    self.PosMotorResponseHigh.Membership = self.FL.FuzzyDisjunction(PosOutputHighRules, sNorm)
    
    # Motor response membership sets must have ComputeArea() called here, since their ComputeMembership() functions are not called, which normally call ComputeArea()
    self.PosMotorResponseLow.ComputeArea()
    self.PosMotorResponseMedLow.ComputeArea()
    self.PosMotorResponseMed.ComputeArea()
    self.PosMotorResponseMedHigh.ComputeArea()
    self.PosMotorResponseHigh.ComputeArea()
    
    # ------- Negative direction sets - CCW rotations, left-wards translation ------- #
    self.NegTiltErrorLarge.ComputeMembership(self.Tilt)
    self.NegTiltErrorMed.ComputeMembership(self.Tilt)
    self.NegTiltErrorSmall.ComputeMembership(self.Tilt)
    
    self.NegTiltIntegralHigh.ComputeMembership(self.TiltIntegral)
    self.NegTiltIntegralMed.ComputeMembership(self.TiltIntegral)
    self.NegTiltIntegralLow.ComputeMembership(self.TiltIntegral)
    
    self.NegWindHigh.ComputeMembership(self.WindSpeed)
    self.NegWindMed.ComputeMembership(self.WindSpeed)
    self.NegWindLow.ComputeMembership(self.WindSpeed)
    
    # (Re)initialize MotorResponseRules
    NegOutputLowRules = []
    NegOutputMedLowRules = []
    NegOutputMedRules = []
    NegOutputMedHighRules = []
    NegOutputHighRules = []
    
    # TiltErrorSmall --> MotorResponseMagnitudeLow
    NegOutputLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.NegTiltErrorSmall.Membership, 1, ImplicationMethod))
    
    # TiltErrorSmall and WindLow --> MotorResponseMagnitudeLow
    #NegOutputLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod))
    
    # TiltErrorSmall and WindMed --> MotorResponseMagnitudeLow
    #NegOutputLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod))
    
    self.NegMotorResponseLow.Membership = self.FL.FuzzyDisjunction(NegOutputLowRules, sNorm)
    
    # TiltErrorSmall and WindHigh --> MotorResponseMagnitudeMedLow
    #NegOutputMedLowRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorSmall.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod))
    
    self.NegMotorResponseMedLow.Membership = self.FL.FuzzyDisjunction(NegOutputMedLowRules, sNorm)
    
    # TiltErrorMed --> MotorResponseMagnitudeMed
    NegOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.NegTiltErrorMed.Membership, 1, ImplicationMethod))
    
    # PosTiltIntegralLow --> MotorResponseMagnitudeMed
    NegOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.PosTiltIntegralLow.Membership, 1, ImplicationMethod))
    
    # TiltErrorMed and WindLow --> MotorResponseMagnitudeMed
    #NegOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod))
    
    # TiltErrorMed and WindMed --> MotorResponseMagnitudeMed
    #NegOutputMedRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod))
    
    self.NegMotorResponseMed.Membership = self.FL.FuzzyDisjunction(NegOutputMedRules, sNorm)
    
    # TiltErrorMed and WindHigh --> MotorResponseMagnitudeMedHigh
    #NegOutputMedHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorMed.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod))
    
    # TiltErrorLarge and WindLow --> MotorResponseMagnitudeMedHigh
    #NegOutputMedHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindLow.Membership], tNorm), 1, ImplicationMethod))
    
    # PosTiltIntegralMed --> MotorResponseMagnitudeMedHigh
    NegOutputMedHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.PosTiltIntegralMed.Membership, 1, ImplicationMethod))
    
    self.NegMotorResponseMedHigh.Membership = self.FL.FuzzyDisjunction(NegOutputMedHighRules, sNorm)
    
    # TiltErrorSmall --> MotorResponseMagnitudeHigh
    NegOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.NegTiltErrorLarge.Membership, 1, ImplicationMethod))
    
    # PosTiltIntegralHigh --> MotorResponseMagnitudeHigh
    NegOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.NegTiltIntegralHigh.Membership, 1, ImplicationMethod))
    
    # TiltErrorLarge and WindMed --> MotorResponseMagnitudeHigh
    #NegOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindMed.Membership], tNorm), 1, ImplicationMethod))
    
    # TiltErrorLarge and WindHigh --> MotorResponseMagnitudeHigh
    #NegOutputHighRules.append(self.FL.ImplicationAntecedant2Consequent(self.FL.FuzzyConjunction([self.NegTiltErrorLarge.Membership, self.NegWindHigh.Membership], tNorm), 1, ImplicationMethod))
    
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
    
    # Linear, robot body kinematics and dynamics
    self.Acceleration = self.MotorForce / self.BotMass
    self.Position += (self.Velocity * self.dt) + (0.5 * (self.Acceleration) * (self.dt ** 2))
    self.Velocity += self.Acceleration * self.dt
    
    self.AccelerationHistory.append(self.Acceleration)
    self.PositionHistory.append(self.Position)
    self.VelocityHistory.append(self.Velocity)
    
    # Angular, rod kinematics and dynamics
    GravitationalTorque = self.Gravity * self.RodMass * np.sin(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    AccelerationTorque = -1*self.Acceleration * self.RodMass * np.cos(self.Tilt * np.pi / 180.0) * (self.RodLength / 2.0)
    WindTorque = self.WindSpeed * self.RodLength * np.sin(self.Tilt * np.pi / 180.0) * self.RodDragCoefficient * (self.RodLength/2.0)
    TotalTorque = GravitationalTorque + AccelerationTorque + WindTorque
    
    self.GravitationalTorqueHistory.append(GravitationalTorque)
    self.AccelerationTorqueHistory.append(AccelerationTorque)
    self.WindTorqueHistory.append(WindTorque)
    self.TotalTorqueHistory.append(TotalTorque)
    
    #print ("GravitationalTorque", "AccelerationTorque", "WindTorque", "TotalTorque")
    #print (GravitationalTorque, AccelerationTorque, WindTorque, TotalTorque)

    self.AngularAcceleration = TotalTorque / self.RodMomentOfInertia
    self.Tilt = (self.Tilt + (self.AngularVelocity * self.dt) + (0.5 * self.AngularAcceleration * (self.dt ** 2))) # % 360
    self.AngularVelocity += self.AngularAcceleration * self.dt
    
    self.AngularAccelerationHistory.append(self.AngularAcceleration)
    self.TiltHistory.append(self.Tilt)
    self.AngularVelocityHistory.append(self.AngularVelocity)
    
    self.TiltIntegral += self.Tilt * self.dt
    
  def IterateSimulation(self, sNorm, tNorm, ImplicationMethod):
    self.UpdateMechanicalState()
    self.UpdateFuzzySets(sNorm, tNorm, ImplicationMethod)
    self.UpdateControls()


