class PaperGrabber():
  #def __init__(self):
    
  def xmlFeedToTitleIDs(self, FeedDir, FeedNames=[]):
    import xml.etree.ElementTree as ET
    #xmlTree = ET.ElementTree()
    xmlTree = ET.parse(FeedDir + FeedNames[0]).getroot()
    #PapersItems = []
    PaperTitles = []
    PaperIDs = []
    for i, Paper in enumerate(xmlTree.iter('item')):
      #PapersItems.append(Paper)
      Title = Paper.find('title').text
      PaperTitles.append(Title)
      PaperUrl = Paper.find('link').text
      ID = PaperUrl[(PaperUrl.index('arnumber=')+len('arnumber=')):]
      PaperIDs.append(ID)
    return zip(PaperTitles, PaperIDs)

  def TitleIDsToCsv(self, TitleIDs, CsvDir, CsvName):
    # Does NOT support multiple files of the same Title
    import csv
    with open(CsvDir + CsvName, 'w') as f:
      w = csv.writer(f, lineterminator='\n')
      w.writerow(['Titles', 'IDs', 'curl command'])
      for i, (Title, ID) in enumerate(TitleIDs):
        w.writerow([Title, ID, 'curl http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=' + str(ID) + ' > ' + Title.replace(' ', '_') + '.pdf'])
        
  def TitleIDsToGrabberBat(self, TitleIDs, BatDir, BatName, PaperDir):
    import csv
    with open(BatDir + BatName, 'w') as f:
      w = csv.writer(f, lineterminator='\n')
      for i, (Title, ID) in enumerate(TitleIDs):
        w.writerow([('curl -d \'tp=&arnumber=' + str(ID) + '\' \ \n http://ieeexplore.ieee.org/stamp/stamp.jsp' + ' > ' + PaperDir + Title.replace(' ', '_') + '.pdf')])
   
XmlPath = 'C:\\Users\\church\\Documents\\amphetadesk-win-v0.93.1\\amphetadesk-win-v0.93.1\\data\\channels\\'
XmlNames = ['ieeetransactionsoncy.xml']

CsvDir = '.\\'
CsvName = 'TitlesIDs.csv'

BatDir = '.\\'
BatName = 'curlPapers.bat'
PaperDir = 'Papers\\'

PG = PaperGrabber()
TitleIDs = PG.xmlFeedToTitleIDs(XmlPath, XmlNames)
PG.TitleIDsToCsv(PG.xmlFeedToTitleIDs(XmlPath, XmlNames), CsvDir, CsvName)
PG.TitleIDsToGrabberBat(PG.xmlFeedToTitleIDs(XmlPath, XmlNames), BatDir, BatName, PaperDir)