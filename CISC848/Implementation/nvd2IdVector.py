import csv
import sys

# Find suitable maxInt size to accomodate large field sizes in csv file
maxInt = sys.maxsize
Decrement = True
while Decrement:
  Decrement = False
  try:
    csv.field_size_limit(maxInt)
  except OverflowError:
    maxInt = int(maxInt/10)
    Decrement = True


IdsDir = '.\\Data\\CVE\\'
UsedIdsFile = 'randomitems.csv'
ExploitedIdsFile = 'ExploitedIDs.csv'

DataDir = '.\\Data\\CVE\\txt\\'

OutputDir = '.\\Data\\'
ExploitedCsvFile = 'ExploitedIdsVectors.csv'
UnexploitedCsvFile = 'UnexploitedIdsVectors.csv'

def ReadInAllIDs():
  # Read Ids of all vulnerabilities used into an array
  AllIDs = []
  with open(IdsDir + UsedIdsFile, 'r', encoding='ascii', errors="surrogateescape") as file:
    IdReader = csv.reader(file)
    for line in IdReader:
      Entry = line[0]
      IdStop = Entry.index(',')
      AllIDs.append(line[0][2:IdStop-1])
  return sorted(AllIDs, key=lambda Id: Id) # Leaves 10000 < Ids at beginning

def ReadInExploitedIDs():
  # Read Ids of all exploited vulnerabilities
  ExploitIds = []
  with open(IdsDir + ExploitedIdsFile, 'r', encoding='ascii', errors="surrogateescape") as file:
    IdReader = csv.reader(file)
    for line in IdReader:
      ExploitIds.append(line[0])
  return sorted(ExploitIds, key=lambda Id: Id)

def ParseInAllBaseScoreVectors(AllIDs):  
  # Parse NVD entries for vulnerability base score vectors, store in arrays
  csv.field_size_limit(maxInt)
  AllVectors = []
  for Id in AllIDs:
    with open(DataDir + 'all\\' + Id + '.txt', 'r', encoding='ascii', errors="surrogateescape") as file:
      EntryReader = csv.reader(file)
      for line in EntryReader:
        if line == []:
          continue
        if str(line).__contains__('&vector=') and str(line).__contains__('v2-calculator'):
          #print(line)
          VectorStart = str(line).index('&vector=') + len('&vector=') + 1
          VectorEnd = VectorStart + 26
          AllVectors.append(str(line)[VectorStart:VectorEnd])
          #print(AllVectors[-1])
          
  AllIDsVectors = zip(AllIDs, AllVectors)
  return AllIDsVectors
  
def SeperateExploitedBaseScoreVectors(ExploitedIDs):  
  ExploitVectors = []
  csv.field_size_limit(maxInt)
  for Id in ExploitedIDs:
    with open(DataDir + 'exploit\\' + Id + '.txt', 'r', encoding='ascii', errors="surrogateescape") as file:
      EntryReader = csv.reader(file)
      for line in EntryReader:
        if line == []:
          continue
        if str(line).__contains__('&vector=') and str(line).__contains__('v2-calculator'):
          #print(line)
          VectorStart = str(line).index('&vector=') + len('&vector=') + 1
          VectorEnd = VectorStart + 26
          ExploitVectors.append(str(line)[VectorStart:VectorEnd])
          #print(ExploitVectors[-1])
          
  ExploitIdsVectors = zip(ExploitedIDs, ExploitVectors)
  return ExploitIdsVectors

def SeperateUnexploitedBaseScoreVectors(AllIDsVectors, ExploitedIDs):
  UnexploitedIdsVectors = []
  # Populate explicitly unexploited vulnerability vectors
  for Vuln in AllIDsVectors:
    if Vuln[0] not in ExploitedIDs:
      UnexploitedIdsVectors.append(Vuln)
      #print(UnexploitedIdsVectors[-1])
  return UnexploitedIdsVectors
      
def WriteIDsAndVectorsToFiles(UnexploitedIdsVectors, ExploitIdsVectors):
  # Write Ids with base score vectors to csv files
  with open(OutputDir + UnexploitedCsvFile, 'w', newline = '') as Output:
    OutputWriter = csv.writer(Output)
    for Vuln in UnexploitedIdsVectors:
      OutputWriter.writerow([Vuln[0], Vuln[1]])
      
  with open(OutputDir + ExploitedCsvFile, 'w', newline = '') as Output:
    OutputWriter = csv.writer(Output)
    for Vuln in ExploitIdsVectors:
      OutputWriter.writerow([Vuln[0], Vuln[1]])
      
AllIDs = ReadInAllIDs()
ExploitedIDs = ReadInExploitedIDs()
AllIDsVectors = ParseInAllBaseScoreVectors(AllIDs)
ExploitIdsVectors = SeperateExploitedBaseScoreVectors(ExploitedIDs)
UnexploitedIdsVectors = SeperateUnexploitedBaseScoreVectors(AllIDsVectors, ExploitedIDs)
WriteIDsAndVectorsToFiles(UnexploitedIdsVectors, ExploitIdsVectors)