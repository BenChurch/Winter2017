class myParser:
  DataDir = '../Data/html/'
  AllVulnFile = 'AllVulnerabilities.html'
  
  def __init__(self):
    print("Parser instantiated")
    
  def main(self):
    from html.parser import HTMLParser as HP
    class myHTMLParser(HP):
      def HandleStartTag(self, tag, attrs):
        
    #import importlib as il
    AllVulnTree = et.iterparse(self.DataDir + self.AllVulnFile)
    for elem in AllVulnTree:
      print(et.tostring(elem))
    
  