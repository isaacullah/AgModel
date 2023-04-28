#!usr/bin/python
import os
import fnmatch
import re
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import seaborn as sns
##############################
## EDIT THESE VALUES -- They are the parameters to sweep through
v1len = range(3)
v2len = range(3)
v3len = range(3)
BASEPATH = "/home/iullah/Dropbox/Research_Projects/Ag_model/Paper/AM_run1/Amalgamated_stats_files/" # set working directory
skipheader = 0
FILEPATTERNS = ["Experiment*_human_pop_all.csv", "Experiment*_deer_pop_all.csv", "Experiment*_deer_eaten_all.csv", "Experiment*_tot_millet_all.csv",  "Experiment*_numpatches_all.csv", "Experiment*_dom_prop_all.csv"]
labels = ['Total Human Population', 'Total Deer Population', 'Number of Deer Eaten', 'Total Millet Population','Number of Millet Patches Used', 'Proportion of Domestic-Type Millet']
fs = ["Human_Pop_ALL.png", "Deer_Pop_ALL.png", "Deer_Eaten_ALL.png", "Millet_Pop_ALL.png", "Millet_Patches_Used_ALL.png", "Domestic_Millets_ALL.png"]
######## Edit these plot style variables as needed ########
clr = "grey" # color for unit traces
clr2 = "black" # color of mean lines
sns.set_style("ticks") # set plot style with seaborn
sns.set_context("paper", font_scale = 1.5) # set plot context with seaborn
ci = [99.9] # confidence intervals for the varation envelopes around the plot lines (showing the variation between runs)
transp = .3 # set transparencey value
wdth = 2 # width of mean lines
sty = "-" # style of mean lines
es = ["unit_traces"] # set error style
##############################
## DON'T EDIT BELOW THIS LINE
##############################


def natural_sort(l):
    '''sorts strings that contain numbers the way you actually want them sorted'''
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

for FILEPATTERN, label, f in zip(FILEPATTERNS,labels,fs):
    # grab a list of all the agregated stats files
    ogmatches = []
    for root, dirnames, filenames in os.walk(BASEPATH):
      for filename in fnmatch.filter(filenames, FILEPATTERN):
        ogmatches.append(os.path.join(root, filename))
    matches = natural_sort(ogmatches)
    # format the plot with the correct number of subplots
    varlist = list(product(v1len,v2len,v3len))
    fig, axes = plt.subplots((len(v1len) * len(v2len) ), len(v3len), figsize=( len(v3len) * len(v3len) * 2, len(v1len) * len(v2len) * 2 ), sharex = True, sharey= True)
    # fig = plt.figure(figsize=(16,4))
    for i in range(len(varlist)):
        print "Processing file: %s - file %s of %s" % (matches[0].split("/")[-1],i+1, len(varlist))
        all_data1 = np.genfromtxt(matches.pop(0), dtype=float, delimiter=',', skip_header=skipheader).T
        sns.tsplot(all_data1, n_boot=1000, err_style=es, color=clr, ci=ci, alpha=transp, lw=0.5, ax = axes.reshape(-1)[i])
        sns.tsplot(all_data1, n_boot=1000, color=clr2, ls=sty, lw=wdth, ax = axes.reshape(-1)[i])
        axes.reshape(-1)[i].text(100, 375, '%s)' % (i+1));
        axes.reshape(-1)[i].locator_params(axis = 'y', nbins = 4)
        axes.reshape(-1)[i].locator_params(axis = 'x', nbins = 6)
    #plt.tight_layout(pad=2.5)
    plt.tight_layout()
    sns.despine()
    plt.subplots_adjust(left=0.05, bottom=0.05)
    fig.text(0.5, 0.005, 'Simulation Year', ha='center', fontsize = 14)
    fig.text(0.005, 0.5, label, va='center', rotation='vertical', fontsize = 14)
    plt.savefig("%s%s%s" % (BASEPATH, os.sep, "%s.png" % f), dpi = 300)
    plt.close()

