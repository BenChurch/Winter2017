import numpy as np

class FuzzyLogic():
  
  class Trapezoid():                            # Reduces to triangle when LS = RS
    def __init__(self, LF, LS, RS, RF):         # Points are of the form (x,mu) where mu is membership, 0 at feet and 1 at shoulders
      # Left being lesser in x than the right
      self.LeftFoot = LF
      self.LeftShoulder = LS
      self.RightShoulder = RS
      self.RightFoot = RF
      
      self.CrispValue = 0 # Keep this from each membership value recomputation - useful in fuzzy set geometry
      self.Membership = 0.0001 # Membership stays just above 0 to prevent division by 0 in self.ComputeCenterOfArea

      # Can break truncated (by membership value) trapezoid down into these sections
      self.LeftTriangleArea = 0
      self.CenterRectangleArea = 0
      self.RightTriangleArea = 0
      self.Area = 0.0001
      self.COA = 0    # Initialize (probably incorrectly) as 0, immediately compute correct value.
      self.ComputeArea()
      
      # Denominators given small positive factors to prevent division by zero - if self.LeftShoulder[0] = self.LeftFoot[0] self.ComputeMembership cases will not use the large slope anyway
      self.LeftSlope = (self.LeftShoulder[1] - self.LeftFoot[1]) / (self.LeftShoulder[0] - self.LeftFoot[0] + 0.00001)
      self.RightSlope = (self.RightFoot[1] - self.RightShoulder[1]) / (self.RightFoot[0] - self.RightShoulder[0] + + 0.00001)
      
    def ComputeMembership(self, CV):
      self.CrispValue = CV
      if self.CrispValue <= self.LeftFoot[0]:
        self.Membership = 0.0001
        #self.COA = None
        self.ComputeArea()
        return
        
      if self.CrispValue > self.LeftFoot[0] and self.CrispValue < self.LeftShoulder[0]:
        self.Membership = self.LeftFoot[1] + (self.LeftSlope * (self.CrispValue - self.LeftFoot[0]))
        self.ComputeArea()
        return
        
      if self.CrispValue >= self.LeftShoulder[0] and self.CrispValue <= self.RightShoulder[0]:
        self.Membership = 1.0
        self.ComputeArea()
        return
        
      if self.CrispValue > self.RightShoulder[0] and self.CrispValue < self.RightFoot[0]:
        self.Membership = self.RightFoot[1] + (self.RightSlope * (self.CrispValue - self.RightFoot[0]))
        self.ComputeArea()
        return
        
      if self.CrispValue >= self.RightFoot[0]:
        self.Membership = 0.0001
        #self.COA = None
        self.ComputeArea()
        return
    
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
      self.COA = ((self.LeftTriangleArea * LeftTriangleCenter) + (self.CenterRectangleArea * CenterRectangleCenter) + (self.RightTriangleArea * RightTriangleCenter)) / self.Area
    
    def PrintMembershipFunctionToAxes(self, col, axes=None):
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
      if len(Memberships) == 1:
        return Memberships[0]
      else:
        return 0.0001
    if tNorm == 'ab':
      if len(Memberships) > 1:
        return Memberships[0] * self.FuzzyConjunction(Memberships[1:], 'ab')
      if len(Memberships) == 1:
        return Memberships[0]
      else:
        return 0.0001
    if tNorm == 'max(a,a+b-1)':
      if len(Memberships) > 1:
        return max(Memberships[0],Memberships[0]+self.FuzzyConjunction(Memberships[1:], 'max(a,a+b-1)')-1)
      if len(Memberships) == 1:
        return Memberships[0]
      else:
        return 0.0001
    else:
      print("Error - Unknown t-norm passed for FuzzyConjunction")
      return
      
  def FuzzyDisjunction(self, Memberships, sNorm):
    if sNorm == 'max':
      if len(Memberships) > 1:
        return max(Memberships[0], self.FuzzyDisjunction(Memberships[1:], 'max'))
      if len(Memberships) == 1:
        return Memberships[0]
      else:
        return 0.0001
    if sNorm == 'a+b-ab':
      if len(Memberships) > 1:
        b = self.FuzzyDisjunction(Memberships[1:], 'a+b-ab')
        return Memberships[0] + b - (Memberships[0] * b)
      if len(Memberships) == 1:
        return Memberships[0]
      else:
        return 0.0001
    if sNorm == 'min(1,a+b)':
      if len(Memberships) > 1:
        return min(1,Memberships[0]+self.FuzzyDisjunction(Memberships[1:], 'min(1,a+b)'))
      if len(Memberships) == 1:
        return min(1,Memberships[0])  # = Memberships[0]
      else: 
        return 0.0001
    else:
      print("Error - Unknown s-norm passed for FuzzyDisjunction")
      return
      
  def FuzzyImplication(self, AntecedantMembership, ConsequentMembership=1.0, Method=None):
    if Method == 'KD':
      return max(1 - AntecedantMembership, ConsequentMembership)
    else:
      print("Error - Unknown FuzzyImplication method")
      return
        
  def ImplicationAntecedant2Consequent(self, AntecedantMembership, ImplicationTruth=1.0, Method=None):
    # Returns membership of consequent for rule evaluation from AntecedantMembership and the truth of the rule, ImplicationTruth
    if Method == "KD":
      if AntecedantMembership == 0:
        return 0.0001    # Cannot (all) be 0
      else:
        # As true as we must make whichever motor output, given the antecedant - assumes ImplicationTruth = 1
        return AntecedantMembership
    else:
      print("Error - Unknown FuzzyImplication method")
      return
