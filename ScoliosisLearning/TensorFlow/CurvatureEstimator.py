import tensorflow as tf

import numpy as np

import csv
import os

DataSet = 'ControlSets'
DataDir = 'Data/' + DataSet + '/NormalizedCompletedErrors/'
DataFiles = []

for root, dirs, files in os.walk(DataDir):
  DataFiles = files  

LandmarkSets = []
  
for FileName in DataFiles:
  LandmarkSets.append([]) # A new landmark set for each patient
  print(FileName)
  with open(DataDir + FileName, newline = '') as csvfile:
    DataReader = csv.reader(csvfile, delimiter = ',', quotechar = '|')
    LineIterator = 0
    DataRows = []
    BeginTranscribe = False
    for row in DataReader:
      print(row)
      if row[0] == '1':
        BeginTranscribe = True
      if BeginTranscribe:
        LineIterator += 1
        CurrentPoint = [0,0,0]
        for dim in range(3):
          CurrentPoint[dim] = float(row[dim+1])
        LandmarkSets[-1].append(CurrentPoint)
    # ASSERT row contains first Landmark point row, and LineIterator corresponds

for LandmarkSet in LandmarkSets:
  for LandmarkPoint in LandmarkSet:
    print(LandmarkPoint)
  print(' ')
  
print(len(LandmarkSets))

