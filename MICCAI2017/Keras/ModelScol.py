import numpy
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

class ScalePredictor:
  def __init__(self):
    
    
    self.InputDir = '../Data/'
    self.LearningData = 'DeepLearningData.csv'
    self.OutputDir = '../Data/'
    self.PredictionsFile = 'NetworkOutput.csv'

    self.AllInputData = []   # Of the form [SupLeftR, SupLeftA, SupLeftS, SupRightR, SupRightA, SupRightS, LeftR, LeftA, LeftS, RightR, RightA, RightS,
      # InfLeftR, InfLeftA, InfLeftS, InfRightR, InfRightA, InfRightS, SupAntR, SupAntA, SupAntS, InfAntR, InfAntA, InfAntS]
    #self.
  
  def ReadInput(self):
    import csv
    with open(self.InputDir + self.LearningData, 'r') as InputFile:
      InputReader = csv.reader(InputFile, delimiter=',', quotechar='|')
      for row in InputReader:
        self.AllInputData.append(row)
    self.AllInputData.__delitem__(0)  # Remove header row
    self.Inputs = self.AllInputData[:][:-6]
    self.Targets = self.AllInputData[:][-6:]
    print(self.AllInputData)
    print("A")
    
# Run the program
SP = ScalePredictor()
SP.ReadInput()
