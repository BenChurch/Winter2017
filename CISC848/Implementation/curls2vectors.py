# Reads base score vectors from the range of vulnerability entry html pages saved as txt files

import csv

idDir = 'Data/CVE/'
idCsv = 'ExploitedIDs.csv'

EntriesDir = 'Data/NVD/txt/'
siteFiles = []

vectorStringLength = 28

def ReadCveIds():
  # Read in CVE ids to refer to files
  with open(idDir + idCsv, 'r') as IDs:
    idReader = csv.reader(IDs)
    for line in idReader:
      siteFiles.append(str(line)[2:-2] + ".txt")
   
   
def ReadBaseScoreVectors():
  idsWithVectors = [[],[]]
     
  # Parse txt files for base score vectors
  for cveFile in siteFiles:
    with open(EntriesDir + cveFile, 'r') as nvdEntry:
      EntryReader = csv.reader(nvdEntry)
      for line in EntryReader:
        if str(line).__contains__('&vector') and str(line).__contains__('CVE') and str(line).__contains__('v2'):
          #print(str(line))
          idStartIndex = str(line).index('CVE')
          idEndIndex = str(line).index('vector')
          cveID = str(line)[idStartIndex:idEndIndex-1]
          if len(idsWithVectors[0]) == 0 or (idsWithVectors[0][-1]) != cveID:
            vectorStartIndex = str(line).index('vector=') + len('vector=')
            Vector = str(line)[vectorStartIndex:vectorStartIndex+vectorStringLength]
            idsWithVectors[0].append(cveID)
            idsWithVectors[1].append(Vector)
          
#for (ID, Vector) in zip(idsWithVectors[0], idsWithVectors[1]):
#  print (ID, Vector)

ReadCveIds()

ReadBaseScoreVectors()