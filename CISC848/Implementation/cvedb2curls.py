# Checks vulnerability entries from cveDBcsv for viability (not rejected, etc) and generates batch file to retrieve their NVD entries using curl software (to later get their base scores)

import csv

DataDir = './Data/CVE/'
cveDBcsv = 'randomitems.csv'
curlBatExploits = 'GetExploitSites.bat'
curlBatAll = 'GetAllSites.bat'
idscsv = 'ExploitedIDs.csv'
allData = 'AllDB.csv'

# nvdURLbase = 'https://web.nvd.nist.gov/view/vuln/detail?vulnId='
nvdURLbase = 'https://nvd.nist.gov/vuln/detail/'

ExploitedIDs = []
AllIDs = []

def ReadInputWriteCurl():
  with open(DataDir + cveDBcsv, 'r', encoding='ascii', errors="surrogateescape") as db:
    with open(DataDir + allData, 'w', newline = '') as output:
      dbWriter = csv.writer(output)
      dbReader = csv.reader(db)
      for line in dbReader:
        ID = str(line[0][2:line[0].index(',')-1])
        if str(line[0]).__contains__('CVE-') and not str(line[0]).__contains__('** RESERVED **') and not str(line[0]).__contains__('** REJECT **'):
          dbWriter.writerow([ID, "curl " + nvdURLbase + ID + " > txt/" + ID + ".txt"])
          AllIDs.append(ID)
          if line[0].__contains__('EXPLOIT-DB:'): # This is the criteria for classifying a vulnerability as exploited or not
            ExploitedIDs.append(ID)
  
def WriteExploitedIdsToBat():
  # print .bat file commands to grab html pages with curl
  with open(DataDir + curlBatExploits, 'w', newline = '') as output:
    outputWriter = csv.writer(output)
    for ID in ExploitedIDs:
      outputWriter.writerow(["curl " + nvdURLbase + ID + " > txt/exploit/" + ID + ".txt"])
 
def WriteAllIdsToBat():
  # Seperate file for vulnerabilities regardless of exploitation
  with open(DataDir + curlBatAll, 'w', newline = '') as output:
    outputWriter = csv.writer(output)
    for ID in AllIDs:
      outputWriter.writerow(["curl " + nvdURLbase + ID + " > txt/all/" + ID + ".txt"])
 
def WriteAllIdsToCsv():
  # print cve ids in .csv file for easy reference
  with open(DataDir + idscsv, 'w', newline = '') as output:
    outputWriter = csv.writer(output)
    for ID in ExploitedIDs:
      outputWriter.writerow([ID])
    
ReadInputWriteCurl()

WriteExploitedIdsToBat()

WriteAllIdsToBat()

WriteAllIdsToCsv()
