This ReadMe file outlines how the python scripts in this deliverable implement the data workflow.

The workflow starts with Data/CVE/allitems.csv
This file is quite large, so I have not included it with the deliverable. If you are intereste, let me know and I will send you a link to it.
It contains CVE IDs for all vulnerabilities in the NVD, plus lists of external sources which refer to the vulnerability. It does not contain base scores or base score vectors.

From allitems.csv, I manually selected all vulnerabilties from the years 2010 to 2016.
This range of entries is saved in Data/CVE/someitems.csv
This file is also large, so I have not included it either, but will find a way to share it upon request.

The first python script to use is then selectFromCsv.py
It selects a user-defined (at the top of the program) number of lines from the someitems.csv files. The lines are selected randomly, subject to non-duplications, and suitability of the entry (it must not be a reserved but unimplemented ID, for example).
These random rows are saved in Data/CVE/randomitems.csv.

With the random set of CVE entries saved in randonitems.csv, the next step is to parse the entries and generate commands which retrieve the NVD entries corresponding to the CVE IDs.
This is done in cvedb2curls.py. It parses the entries from randonitems.csv, identifies which are exploited by references to the Exploit Database, and generates two .bat files to retrieve the NVD data.
cvedb2curls.py also saves the IDs of the exploited vulnerabilities to Data/CVE/ExploitedIDs.csv for convenient distinction later.
Two .bat files (Data/CVE/GetExploitSites.bat, and Data/CVE/GetAllSites.bat) are used to enable saving the exploited vulnerability entries seperately from all vulnerability entries.
Running these batch files from a console saves all NVD vulnerability .html pages to .txt files in Data/CVE/txt/exploit and Data/CVE/txt/all, respectively.
I have not included these .txt files, again for deliverable size reasons.

Now that vulnerability IDs, and their base scores (in Data/CVE/txt), are availible, nvd2IdVector.py is run. This script saves the IDs conveniently alongside their base score vectors.
nvd2IdVector.py generates two csv files: Data/ExploitedIdsVectors.csv and Data/UnexploitedIdsVectors.csv.
The vulnerability data is now conveniently compartmentalized based on exploitation classification.

With the data represented conveniently as [ID, Base score vector] in csv files, we can begin exploring my actual contribution.

The base score equation parameters are optimized simply by running optimizeParameters.py. The 18 parameters' original values are defined at the top of this file as the search space start.
The base score threshold for predicting a vulnerability's exploitability (classifying as Exploitable?: Yes/No) is also defined at the top of this program. optimizeParameters.py uses
scipy's optimization toolbox's minimize() function on the OptObjFun() function defined in the file. It is in the OptObjFun() where different optimization approaches can be tried. This is where I 
tried to optimize based on the intra-class correlation coefficient (ICC), sensitivity, precision, and variations on them.

These metrics used in optimization are computed with functions imported from vectors2metrics.py, which itself need not be run from the console. First, PredictExploits() should be run
to generate the confusion matrix for the vulnerabilities given the parameter values and threshold passed to it. Then sensitivity, precision, and ICCs can be computed as per
formance metrics. The variable'Fmeasure' is computed as the value the minimization algorithm optimizes on. The Fmeasure was used to combine the performance metrics in various ways,
like a weighted average. The ComputeICC() function may be of interest, as it returns a composite ICC (CompICC), rather than a single one. This is because both the exploited and 
unexploited classes have their own ICCs, both of which matter, however the optimization is performed on a 1D objective function output. CompICC is computed as an average, weighted based on the subjective values of the different classes' ICCs.
optimizeParameters.py also saves the original parameters and their classification performance with the corresponding optimized results in optimizationResults.csv.

With the optimized equation parameters and performance metrics saved, classification improvments can be determined from these results. boxPlot.py reads these results and generates boxplots
comparing the unexploited class of vulnerabilities' base scores to those of the exploited class. Boxplots are produced for the original and optimized base score equations.