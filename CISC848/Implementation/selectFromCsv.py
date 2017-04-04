# Randomly selects user-set number of rows from csv file

import csv, numpy

DataDir = 'Data/CVE/'
SelectFromFile = 'someitems.csv'
OutputFile = 'randomitems.csv'

NumSelections = 10000

# Read all rows from file
AllRows = []
with open(DataDir + SelectFromFile, 'r', encoding='ascii', errors="surrogateescape") as SelectFrom:
  SelectionReader = csv.reader(SelectFrom)
  for line in SelectionReader:
    if not str(line).__contains__('** RESERVED **') and not str(line).__contains__('** REJECT **'):
      #print(line)
      AllRows.append(line)
      
if NumSelections > len(AllRows):
  print("Error - more selctions requested than data availible")

# Select rows randomly from all rows
SelectedRows = []
RemSelections = NumSelections
while RemSelections > 0:
  RandomDeci = numpy.random.uniform()
  RandomIndex = int(RandomDeci * len(AllRows))
  # Second item of tuple allows sorting outcome as AllRows was sorted
  SelectedRows.append((AllRows[RandomIndex], RandomIndex + NumSelections - RemSelections))
  AllRows.__delitem__(RandomIndex)
  RemSelections -= 1
  
SelectedRows.sort(key=lambda Tup: Tup[1])

# Write selected rows to file
with open(DataDir + OutputFile, 'w', newline = '') as output:
  outputWriter = csv.writer(output)
  for Row in SelectedRows:
    outputWriter.writerow([Row][0])