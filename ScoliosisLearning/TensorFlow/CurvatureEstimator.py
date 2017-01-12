
import tensorflow as tf
import numpy as np
import importlib as il
import math, csv, os

DataSet = 'ControlSets'
DataDir = 'Data/' + DataSet + '/NormalizedCompletedErrors/'
DataFiles = []

Vertebrae = ['T1','T2','T3','T4','T5','T6','T7','T8','T9','T10','T11','T12','L1','L2','L3','L4','L5']
LandmarkData = []
TrueCurveCritVert = []

def main():
  ReadData()
  MeasureAngles()
  IdentifyMissingPointsLabels()
  print('Hello')
  
def ReadData():  
  for root, dirs, files in os.walk(DataDir):
    DataFiles = files  
  InputData = []
  for FileName in DataFiles:
    InputData.append([]) # A new landmark set for each patient
    #print(FileName)
    with open(DataDir + FileName, newline = '') as csvfile:
      DataReader = csv.reader(csvfile, delimiter = ',', quotechar = '|')
      LineIterator = 0
      DataRows = []
      BeginTranscribe = False
      for row in DataReader:
        #print(row)
        if row[0] == '1':
          BeginTranscribe = True
        if BeginTranscribe:
          LineIterator += 1
          CurrentPoint = [None,None,None]   # Find a way to accomodate missing points
          for dim in range(3):
            CurrentPoint[dim] = float(row[dim+1])
          InputData[-1].append(CurrentPoint)
          CurrentPoint = [None,None,None]
      # ASSERT row contains first Landmark point row, and LineIterator corresponds

  for Patient in InputData:
    LandmarkData.append([])
    for i, LandmarkPoint in enumerate(Patient):
      if i % 2 == 0:
        # If i is even, the TrP is a left-sided one
        LandmarkData[-1].append([]) # One 3-element list for each vertebra
        LandmarkData[-1][-1].append(Vertebrae[int(i/2)])  # 1st element: label
        LandmarkData[-1][-1].append(LandmarkPoint)        # 2nd element: left point coord
      else:
        LandmarkData[-1][-1].append(LandmarkPoint)        # 3rd: right coord
        #print(LandmarkData[-1][-1])
    print('')
    
def MeasureAngles():
  for Patient in LandmarkData:
    MinAngle = 180
    MinVertebra = ''
    MaxAngle = -180
    MaxVertebra = ''
    RightLeftVector = [0,0,0]
    for i, Vertebra in enumerate(Patient):
      for dim in range(3):
        RightLeftVector[dim] = Vertebra[2][dim] - Vertebra[1][dim]
      RightLeftVector[1] = 0  # Project onto coronal plane
      VertebraAngle = (180/math.pi) * math.acos((np.dot(RightLeftVector, [1,0,0])) / (np.linalg.norm(RightLeftVector)))
      if Vertebra[1][2] < Vertebra[2][2]:
        VertebraAngle = -1 * VertebraAngle
      if VertebraAngle > MaxAngle:
        MaxAngle = VertebraAngle
        MaxVertebra = Vertebrae[i]
      elif VertebraAngle < MinAngle:
        MinAngle = VertebraAngle
        MinVertebra = Vertebrae[i]
      Angle = MaxAngle - MinAngle
    if Vertebrae.index(MinVertebra) > Vertebrae.index(MaxVertebra):
      # MinVertebra is inferior to MaxVertebra
      TrueCurveCritVert.append([-Angle, MinVertebra, MaxVertebra])
    else:
      TrueCurveCritVert.append([Angle, MaxVertebra, MinVertebra])
    print(TrueCurveCritVert[-1])
    
def IdentifyMissingPointsLabels():
  print('')