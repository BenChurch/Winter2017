This ReadMe file outlines how the python scripts in this deliverable implement the data workflow.

The workflow starts with Data/CVE/allitems.csv
It contains CVE IDs for all vulnerabilities in the NVD, plus lists of external sources which refer to the vulnerability. It does not contain base scores or base score vectors.

From allitems.csv, I manually selected all vulnerabilties from the years 2010 to 2016.
This range of entries is saved in Data/CVE/someitems.csv

The first python script to use is then selectFromCsv.py
It selects a user-defined (at the top of the program) number of lines from the someitems.csv files. The lines are selected randomly, subject to non-duplications, and suitability of the entry (it must not be a reserved but unimplemented ID, for example).
These random rows are saved in Data/CVE/randomitems.py.