import csv

IdsDir = 'C:\\Users\\Ben\\Documents\\Masters16_17\\848Data\\CVE\\'
UsedIdsFile = 'randomitems.csv'
ExploitedIdsFile = 'ExploitedIDs.csv'

DataDir = 'C:\\Users\\Ben\\Documents\\Masters16_17\\848Data\\NVD\\txt\\'

OutputDir = 'C:\\Users\\Ben\\Documents\\Masters16_17\\848Data\\NVD\\csv\\'
ExploitedCsvFile = 'ExploitedIdsVectors.csv'
UnexploitedCsvFile = 'UnexploitedIdsVectors.csv'


# Read Ids of all vulnerabilities used into an array
AllIds = []
with open(IdsDir + UsedIdsFile, 'r', encoding='ascii', errors="surrogateescape") as file:
  IdReader = csv.reader(file)
  for line in IdReader:
    Entry = line[0]
    IdStop = Entry.index(',')
    AllIds.append(line[0][2:IdStop-1])
    
AllIds.sort(key=lambda Id: Id) # Leaves 10000 < Ids at beginning

# Read Ids of all exploited vulnerabilities
ExploitIds = []
with open(IdsDir + ExploitedIdsFile, 'r', encoding='ascii', errors="surrogateescape") as file:
  IdReader = csv.reader(file)
  for line in IdReader:
    ExploitIds.append(line[0])

ExploitIds.sort(key=lambda Id: Id)

AllVectors = []
# Read vulnerability base score vectors into arrays
for Id in AllIds:
  with open(DataDir + 'all//' + Id + '.txt', 'r', encoding='ascii', errors="surrogateescape") as file:
    EntryReader = csv.reader(file)
    for line in EntryReader:
      if line == []:
        continue
      if str(line).__contains__('&vector='):
        #print(line)
        VectorStart = str(line).index('&vector=') + len('&vector=') + 1
        VectorEnd = VectorStart + 26
        AllVectors.append(str(line)[VectorStart:VectorEnd])
        #print(AllVectors[-1])
        
AllIdsVectors = zip(AllIds, AllVectors)

ExploitVectors = []
for Id in ExploitIds:
  with open(DataDir + 'exploit//' + Id + '.txt', 'r', encoding='ascii', errors="surrogateescape") as file:
    EntryReader = csv.reader(file)
    for line in EntryReader:
      if line == []:
        continue
      if str(line).__contains__('&vector='):
        #print(line)
        VectorStart = str(line).index('&vector=') + len('&vector=') + 1
        VectorEnd = VectorStart + 26
        ExploitVectors.append(str(line)[VectorStart:VectorEnd])
        #print(ExploitVectors[-1])
        
ExploitIdsVectors = zip(ExploitIds, ExploitVectors)

UnexploitedIdsVectors = []
# Populate explicitly unexploited vulnerability vectors
for Vuln in AllIdsVectors:
  if Vuln[0] not in ExploitIds:
    UnexploitedIdsVectors.append(Vuln)
    print(UnexploitedIdsVectors[-1])
    
# Write Ids with base score vectors to csv files
with open(OutputDir + UnexploitedCsvFile, 'w', newline = '') as Output:
  OutputWriter = csv.writer(Output)
  for Vuln in UnexploitedIdsVectors:
    OutputWriter.writerow([Vuln[0], Vuln[1]])
    
with open(OutputDir + ExploitedCsvFile, 'w', newline = '') as Output:
  OutputWriter = csv.writer(Output)
  for Vuln in ExploitIdsVectors:
    OutputWriter.writerow([Vuln[0], Vuln[1]])