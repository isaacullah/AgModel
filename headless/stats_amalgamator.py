#!usr/bin/python
import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import seaborn as sns
##############################
## EDIT THESE VALUES -- They are the parameters to sweep through
v1len = range(3)
v2len = range(3)
v3len = range(3)
repeats = 100
basepath = os.getcwd()
skipheader = 1
header = "human_pop"
label = 'Total Human Population'
col = 3
## DON'T EDIT BELOW THIS LINE
##############################
varlist = list(product(v1len,v2len,v3len))
fig, axes = plt.subplots((len(v1len) * len(v2len) ), len(v3len), figsize=( len(v3len) * len(v3len) * 2, len(v1len) * len(v2len) * 2 ), sharex = True, sharey= True)
#fig = plt.figure(figsize=(16,4))
for i in range(len(varlist)):
    print "Processing stats file %s of %s" % (i+1, len(varlist))
    sfs = ['%s%sSimulation_general_stats.%s.%s.csv' % (basepath, os.sep, i + 1, str(x).zfill(len(str(repeats)))) for x in range(repeats)]
    all_data = np.genfromtxt(sfs.pop(0), dtype=float, delimiter=',', skip_header=skipheader, usecols=(col-1))
    for match in sfs:
        data = np.genfromtxt(match, dtype=float, delimiter=',', skip_header=skipheader, usecols=(col-1))
        all_data = np.vstack((all_data, data))
    np.savetxt("%s%s%s" % (basepath, os.sep, "Experiment%s_%s_all.csv" % (i + 1, header)), all_data.T, delimiter=",")
    #ax = fig.add_subplot((len(v1len) * len(v2len) ), len(v3len), i+1)
    sns.tsplot(all_data, err_style="unit_traces", ax = axes.reshape(-1)[i])
    axes.reshape(-1)[i].text(0.1, 0.9, '%s)' % (i+1));
    #sns.axlabel("Years", "Proportion of Domestic-type Millet", fontsize=12);
    #plt.legend(loc=0);
    #p1 = plt.plot(all_data, color=c1, alpha=0.3, linewidth=1.5)
    #p5 = plt.plot(all_data.mean(1), color=c1, alpha=1, linewidth=1.8, label="Experiment %s" % i + 1)
    #leg = plt.legend(loc=4, prop={'size':12})
    #for legobj in leg.legendHandles:
        #legobj.set_linewidth(2.0)
    #ax = plt.axis([0, 5000, 0, 1.0])
    #plt.axhline(linewidth=2, color = "black")
    #plt.axvline(linewidth=1, color = "black")
    #ticks = plt.yticks([x / 10.0 for x in range(0, 10, 1)])
    #plt.xlabel('Years', fontsize=12)
    #plt.ylabel('Proportion of Domestic-type Millet', fontsize=12)
#plt.subplots_adjust(hspace=0.001)
plt.tight_layout(pad=2.5)
#sns.axlabel("Years", "Proportion of Domestic-type Millet", fontsize=12)
fig.text(0.5, 0.005, 'Years', ha='center', fontsize = 14)
fig.text(0.005, 0.5, label, va='center', rotation='vertical', fontsize = 14)
plt.savefig("%s%s%s" % (basepath, os.sep, "All_%s.png" % header), dpi = 300)
plt.close()

