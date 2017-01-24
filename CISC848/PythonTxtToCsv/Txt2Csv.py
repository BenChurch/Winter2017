class TextReader:
  DataDir = '../Data/txt/'
  InputFileName = 'trial.txt'
  OutputFileName = 'ScoredVulnerabilities.csv'
  
  def __init__(self):
    print("TextReader instantiated")
    self.VulnerabilityIDs = []  # Will contain all non-empty text lines from InputFile
    self.VulnerabilityDescs = []
    
  def main(self):
    import csv
    with open(self.DataDir + self.InputFileName) as f:
      reader = csv.reader(f)
      for i, line in enumerate(reader):
        #print(line)
        if line == [] or len(line[0]) < 6: # Too short to contain Name field, continue to avoid out-of-range error
          continue
        if line[0][0:2] == '**':  # Could be the Name field  
          if line[0][0:6] == '**Name':
            self.VulnerabilityIDs.append(line[0][9:-2])  # Should contain CVE-####-####
            continue
          elif line == ['**Description:**  ']:
            self.VulnerabilityDescs.append([])
            DescReader = csv.reader(f)
            DescReader.line_num
            for DescLine in DescReader:
              if DescLine == []:
                break # End of vulnerability description - break loop
              else:
                self.VulnerabilityDescs[-1] = self.VulnerabilityDescs[-1] + DescLine[0]
    
    for Vuln in range(len(self.VulnerabilityIDs)):
      print(self.VulnerabilityIDs[Vuln] + " ### " + self.VulnerabilityDescs[Vuln])
      
        
