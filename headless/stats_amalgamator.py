#!usr/bin/python
import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import seaborn as sns
##############################
## EDIT THESE VALUES -- They are the parameters to sweep through
# of these length should be the number of variable values used in parallelizer.pu)
v1len = range(3)
v2len = range(1)
v3len = range(1)
repeats = 10
basepath = os.getcwd()
skipheader = 1
# this is the column to amalgamate
header = "human_pop"
label = 'Total Human Population'
col = 3
## DON'T EDIT BELOW THIS LINE
##############################
varlist = list(product(v1len,v2len,v3len))
for i in range(len(varlist)):
    print("Processing stats file %s of %s" % (i+1, len(varlist)))
    sfs = ['%s%sSimulation_general_stats.%s.%s.csv' % (basepath, os.sep, i + 1, str(x).zfill(len(str(repeats)))) for x in range(repeats)]
    all_data = np.genfromtxt(sfs.pop(0), dtype=float, delimiter=',', skip_header=skipheader, usecols=(col-1))
    for match in sfs:
        data = np.genfromtxt(match, dtype=float, delimiter=',', skip_header=skipheader, usecols=(col-1))
        all_data = np.vstack((all_data, data))
    np.savetxt("%s%s%s" % (basepath, os.sep, "Experiment%s_%s_all.csv" % (i + 1, header)), all_data.T, delimiter=",")


