class TextReader:
  DataDir = '../Data/txt/'
  InputFileName = 'trial.txt'
  OutputFileName = 'IDsWithDescriptions.csv'
  
  def __init__(self):
    print("TextReader instantiated")
    self.VulnerabilityIDs = []  # Will contain all non-empty text lines from InputFile
    self.VulnerabilityDescs = []
    
  def main(self):
    import csv
    with open(self.DataDir + self.InputFileName) as f:
      reader = csv.reader(f, quotechar=None)
      Describing = False
      for line in reader:
        #print(line)
        if Describing:
          if line == []:
            Describing = False
            continue
          else:
            self.VulnerabilityDescs[-1] = self.VulnerabilityDescs[-1] + line[0] 
        if (line == []): 
          continue
        if (len(line[0]) < 6) and not Describing: # Too short to contain Name field, continue to avoid out-of-range error
          continue
        if line[0][0:6] == '**Name':
          self.VulnerabilityIDs.append(line[0][8:-2])  # Should contain 'CVE-####-####'
          continue
        if line == ['**Description:**  ']:
          Describing = True
          self.VulnerabilityDescs.append('')
          continue    # Need to get to next line before appending description
        
    with open(self.DataDir + self.OutputFileName, 'w', newline='') as f:
      writer = csv.writer(f, delimiter=',')
      writer.writerow(['CVE IDs', 'Vulnerability descriptions'])
      for Vuln in range(len(self.VulnerabilityIDs)):
        writer.writerow([self.VulnerabilityIDs[Vuln], self.VulnerabilityDescs[Vuln]])

