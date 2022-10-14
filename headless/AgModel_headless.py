#!usr/bin/python

# Model Description
############################
# This model simulates a complex hunter-gatherer band making optimal foraging decisions between a high-ranked resource and a low-ranked resource. The high-ranked resource is rich, but hard to find and proces,and potentially very scarce. The low-ranked resource is poor, but common and easy to find and process.
# !! THIS VERSION RUNS HEADLESS (NO GUI), AND CAN BE LOOPED BY AN EXTERNAL PROGRAM !!

## Notes
#    Low-ranked resource parameterized for millet.
#    Domestic millet produces 1014 kcal/kg, yielding 1000 kg/ha from seeds dispersed at 10 kg/ha, with 176,000 seeds per kilogram (so 1.76 million plants per ha), and a return rate of about 500 kcal/hr once encountered. Assume patch size is one hectare. Data from FAO: http://www.fao.org/ag/AGP/AGPC/doc/gbase/data/pf000280.htm
#     Wild millet: Right now, just assuming everything is half as much as domestic millet.
# High ranked resource parameterized as deer, producing 1580 kcal/kg, with 100 kg yield per animal, and a return rate of abotu 10000 kcal/hr once encountered. Assuming two fawns per year and three days average search time when there are 1000 animals in the vicinity. Some of these are estimates from Bettinger 1991, and some come from USDA nutrition info for vennison.
#Note that this model assumes storage of millet, but not of deer

#Changelog:
    # v0.3 to v0.4
    # upgrade to Python 3
    # selection is now balanced against diffusion in utilized patches.
    # diffusion is now density dependent, so that it reduces as the percentage of domestic phenotype in the ecosystem increases.
    # added docstrings to classes and functions (no functional changes)
    # added variable 'cultiv' to the sparse CLI for added functionality

# DO NOT EDIT BELOW THIS LINE
#########################################################################################################################################


import os
import sys
import numpy as np
import pandas as pd
import argparse

#Set up sparse CLI
parser = argparse.ArgumentParser(description='This model simulates a complex hunter-gatherer band making optimal foraging decisions between a high-ranked resource and a low-ranked resource. The high-ranked resource is rich, but hard to find and proces,and potentially very scarce. The low-ranked resource is poor, but common and easy to find and process.')
parser.add_argument('--hbirth', metavar='0.032', type=float, nargs='?', const=.032, default=.032, help='Enter the annual human per capita birth rate')
parser.add_argument('--mselect', metavar='0.03', type=float, nargs='?', const=.03, default=.03, help='Enter the coefficient of slection (e.g., the rate of change from wild-type to domestic type)')
parser.add_argument('--cultiv', metavar='2000', type=int, nargs='?', const=2000, default=2000, help='Enter the number of additional millet plants to added to a patch each year due to proto cultivation of the patch. The patch reduces by the same number if not exploited.')
parser.add_argument('--label', metavar='Z.ZZ', nargs='?', const='1.01', default='1.01', help='This is the experiment and run number. E.g., experiment 1, run 1, should look like: 1.01')
###############################################################
## EDIT THESE VARIABLES AS YOU SEE FIT
# HUMAN VARIABLES
people = 50         ## Enter the initial number of people in the band
maxpeople = 500    ## Enter the maximum human population (just to keep this in the realm of possibility, and to help set the y axis on the plot)
#THIS COMES FROM CLI NOW hbirth = 0.033         ## Enter the annual human per capita birth rate
hdeath = 0.03        ## Enter the annual human per capita death rate
starvthresh = 0.8    ## Enter the starvation threshold (percentage of the total kcal below which people are starving, and effective reproduction goes to 0)
hkcal = 547500.0 #for a 1500 kcal diet,730000.0 for a 2000kcal diet, or 1095000.0 for a 3000kcal diet    ## Enter the number of kcals per year rquired per person
fhours = 4380        ## Enter the number of foraging hours available per person
hgratio = 0.35        ## Enter the ratio of hunters to gatherers in the population (allocates foraging type efforts)
# DEER VARIABLES
deer = 4000         ## Enter the inital number of deer in the hunting region
maxdeer = 6000     ## Enter the maximum number of deer that the region can sustain (carrying capacity) without human predation
dmigrants = 10        ## Enter the number of new deer that migrate into the territory each year (keeps deer pop from being totally wiped out)
dbirth = 0.065        ## Enter the annual per capit birth rate for deer
ddeath = 0.02        ## Enter the annual per capita natural death rate for deer
dret = 158000.0        ## Enter the return rate (number of kcals) per deer killed
ddsrch = 72.0        ## Enter the density dependent search costs for deer (hours time expended per recovery of one deer at the density "ddens")
ddens = 1000        ## Density of deer for which search cost "dsrch" is known
dpatch = 1.0        ## Number of individual deer encountered per discovery
dhndl = 25.0        ## Enter the handling costs for deer (hours handling time expended per deer once encountered)
# MILLET VARIABLES
millet = 750        ## Enter the number of millet patches in the gathering region (assume a patch is ~1ha)
#mout = 100.0        ## Enter the viable seed yield per plant
#mdud = .99        ## Enter the proportion of seeds that don't germinate due to predation or improper emplantation
mretw = 0.0507        ## Enter the return rate (number of kcals) per wild-type millet seed
mretd = 0.1014        ## Enter the return rate (number of kcals) per domestic-type millet seed
mprop = 0.98        ## Enter the starting proportion of wild-type to domestic-type millet (1.0 = all wild, 0.0 = all domestic)
#THIS COMES FROM CLI NOW mselect = 0.03        ## Enter the coefficient of slection (e.g., the rate of change from wild-type to domestic type)
mdiffus = 0.01        ## Enter the coefficient of diffusion for millet (the rate at which selected domestic traits dissappear due to crossbreeding)
msrch = 1.0        ## Enter the search costs for millet (hours expended to find one patch of millet)
mpatch = 880000    ## Number of millet plants per patch at the start of the simulation (individuals encountered per discovery)
maxpatch = 1760000 ## Maximum number of millet plants that can be grown per patch (a bit of a teleology, but we need a stopping point for now)
mhndlw = 0.0001        ## Enter the handling costs for wild millet (hours handling time expended per seed once encountered)
mhndld = 0.00005        ## Enter the handling costs for domestic millet (hours handling time expended per seed once encountered)
# SIMULATION CONTROLS
years = 5000        ## Enter the number of years for which to run the simulation
texton = False        ## True will run with output text to the terminal, false will run with without text output

# DO NOT EDIT BELOW THIS LINE
#############################################################

#Get values from command line variables
args = vars(parser.parse_args())
hbirth = args["hbirth"]
mselect = args["mselect"]
cultiv = args["cultiv"]
label = args["label"]
#Make some custom functions for the population dynamics

def babymaker(p, n): #p is the per capita birth rate, n is the population size
    """This is a class to pick the number of births in a given year. p is the per capita birth rate, n is the population size."""
    babys = 0
    for m in range(int(n)):
        x = np.random.random()
        if x < float(p):
            babys = babys + 1
    return(babys)

def deathdealer(p, n): #p is the per capita death rate, n is the population size
    """This is a class to pick the number of deaths in a given year. p is the per capita death rate, n is the population size."""
    deaths = 0
    for m in range(int(n)):
        x = np.random.random()
        if x < float(p):
            deaths = deaths + 1
    return(deaths)


if __name__ == "__main__":
    ##### Setup the simulation
    milletpatches = []
    for patch in range(int(millet)): # set up a data container for our millet patches. They will all start out the same.
        milletpatches.append([mpatch, mprop])
    millet_df = pd.DataFrame(milletpatches, columns=['mpatch','mprop']) # turn this data container into a pandas dataframe for more efficient math and indexing
    patchdens_ts = pd.DataFrame(index=list(range(1,int(millet+1))), columns=list(range(years+1))) # set up a blank pandas dataframe to catch patch density timeseries stats for possible output
    patchprop_ts = pd.DataFrame(index=list(range(1,int(millet+1))), columns=list(range(years+1))) # set up a blank pandas dataframe to catch patch domestic proportion timeseries stats for possible output
    patchdens_ts[0] = millet_df.mpatch # update with year 0 data
    patchprop_ts[0] = millet_df.mprop # update with year 0 data
    # set up some individual data containers for the output stats and plots
    yr = [0]
    hpop = [people]
    hkcald = [0]
    dpop = [deer]
    mpop = [(millet * mpatch)/1000.]
    dkil = [0]
    mexp = [0]
    mdom = [1 - mprop]
    mdens = [mpatch/1000]
    ####### The simulation starts here.
    for year in range(1,years+1):        #this is the outer loop, that does things at an annual resolution, counting the years down for the simulation
        if texton == True: print("Year: %s" % year)
        kcalneed = people * hkcal        # find the number of kcals needed by the band this year
        htimebudget = people * fhours * hgratio        # find the hunting time budget for the band this year
        gtimebudget = people * fhours * (1/hgratio)    # find the gathering time budget for the band this year ##NOTE- excess hunting time will be used for gathering
        deer_now = deer            #set up a variable to track deer population exploitation this year
        millet_now = millet        #set up a variable to track millet patch exploitation this year
        eatmillet = 0        #set up data container to count how many millet patches we ate this year
        eatdeer = 0        #set up dat container to count how many deer we ate this year
        while kcalneed > 0:        #this is the inner loop, doing foraging within the year, until kcal need is satisfied
            if deer_now <= 0 and millet_now <= 0:
                if texton == True: print("Ate everything!!!")
                break
            #first calculate info about the current state of millet
            mprop_now = np.mean(millet_df.mprop[0:millet_now]) #Note that we are taking the mean proportion acoss all remaining millet patches in the data array.
            mpatch_now = np.mean(millet_df.mpatch[0:millet_now]) #Note that we are taking the mean number of individuals perpatch across all remaining patches in the millet data array. Note that we are reading off of the right end of the array list.
            mret = (mretw * mprop_now) + (mretd * (1 - mprop_now))        #determine the actual kcal return for millet, based on the proportion of wild to domesticated.
            mhndl = (mhndlw * mprop_now) + (mhndld * (1 - mprop_now))    #determine the actual handling time for millet, based on the proportion of wild to domesticated.
            if deer_now <= 0:
                deerscore = 0
            else:
                dsrch_now = ddsrch / (deer_now / ddens)        #find the actual search time for the amount of deer at this time
                deerscore = dret / (dsrch_now + (dhndl * dpatch))    #find the current return rate (kcal/hr) for deer.
            if millet_now <= 0:
                milletscore = 0
            else:
                milletscore = (mret * mpatch_now ) / (msrch + (mhndl *  mpatch_now))        #find the current return rate (kcal/hr for millet.
            #if texton == True; print deerscore, milletscore, kcalneed
            if deerscore >= milletscore:        #check to see whether the band should eat deer or millet at this moment
                ## eating deer, so update data containers accordingly
                if htimebudget <= 0:
                    if texton == True: print("Ran out of hunting time this year, hopefully there is gathering time left")
                    deerscore = 0
                    pass
                if deer_now <= 0: #if they killed all the deer, then go to millet if possible
                    if texton == True: print("Killed all the deer available this year, will try to make up the remainder of the diet with millet")
                    deerscore = 0.
                    pass
                else:
                    kcalneed = kcalneed - dret ## QUESTION: should this be the return for a deer minus the search/handle costs?? Or is that included in the daily dietary need (i.e., the energy expended searching and processing foodstuffs)
                    htimebudget = htimebudget - (dsrch_now + (dhndl * dpatch))
                    eatdeer = eatdeer + dpatch
                    deer_now = deer_now - dpatch
            else: ## eating millet, so update data containers accordingly
                if gtimebudget <= 0:
                    if texton == True: print("Ran out of gathering time this year, hopefully there is hunting time left")
                    milletscore = 0
                    pass
                elif gtimebudget <= 0 and htimebudget > 0:
                    if texton == True: print("Using remaining hunting time to gather millet")
                    kcalneed = kcalneed - (mret * mpatch_now)
                    htimebudget = htimebudget - msrch - (mhndl * mpatch_now)
                    eatmillet = eatmillet + 1
                    millet_now = millet_now - 1
                elif gtimebudget <=0 and htimebudget <= 0:
                    if texton == True: print("Not enough hunting time left to use for gathering")
                    milletscore = 0
                    pass
                else: pass
                if millet_now <= 0: #if millet is all gone, then go back to deer
                    if texton == True: print("Harvested all available millet this year, will try to make up the remainder of the diet with deer.")
                    milletscore = 0
                    pass
                else:
                    kcalneed = kcalneed - (mret * mpatch_now)
                    gtimebudget = gtimebudget - msrch - (mhndl * mpatch_now)
                    eatmillet = eatmillet + 1
                    millet_now = millet_now - 1
            if htimebudget <= 0 and gtimebudget <= 0:        #check if they've run out of foraging time, and stop the loop if necessary.
                if texton == True: print("Ran out of all foraging time for this year before gathering enough food.")
                break
            if deer <= 0 and millet <= 0:    #check if they've run out of food, and stop the loop if necessary.
                if texton == True: print("Ate all the deer and all the millet this year before gathering enough food.")
                break
            if deerscore <= 0 and milletscore <= 0:    #check if they've run out of food, and stop the loop if necessary.
                if texton == True:print("Ate all the deer and all the millet this year before gathering enough food.")
                break
        ####### Now that the band has foraged for a year, update human, deer, and millet populations, and implement selection
        if (people * hkcal) - kcalneed <= (people * hkcal * starvthresh):     #Check if they starved this year and just die deaths if so
            if texton == True: print("Starved a bit this year, no births will occur.")
            people = people - deathdealer(hdeath, people)
        else: #otherwise, balance births and deaths, and adjust the population accordingly
            people = people + babymaker(hbirth, people) - deathdealer(hdeath, people)
        deer = deer_now + babymaker(dbirth, deer_now) - deathdealer(ddeath, deer_now) + dmigrants #Adjust the deer population by calculating the balance of natural births and deaths on the hunted population, and then add the migrants population
        if people > maxpeople: people = maxpeople # don't allow human pop to exceed the limit we set
        if deer > maxdeer: deer = maxdeer # don't allow deer pop to exceed natural carrying capacity
        #This part is a bit complicated. We are adjusting the proportions of wild to domestic millet in JUST the millet patches that were exploited this year. We are also adjusting the density of individuals in those patches. This is the effect of the "artifical selection" exhibited by humans while exploiting those patches. At the same time, we are implementing a "diffusion" of wild-type characteristics back to all the patches. If they are used, selection might outweigh diffusion. If they aren't being used, then just diffusion occurs. In this version of the model, diffusion is density dependent, and is adjusted by (lat year's) the proportion of domestic to non-domestic millets left in the population.
        patch_adjust = [] # make a matrix to do the selection/diffusion on the individual patches based on if they got used or not.
        currentmdiffus = mdiffus * (1 - mdom[-1])
        for x in range(1,int(millet+1)):
            if x < eatmillet:
                patch_adjust.append([currentmdiffus-mselect, cultiv])
            else:
                patch_adjust.append([currentmdiffus, -cultiv])
        patch_adjustdf = pd.DataFrame(patch_adjust, columns=['sel', 'cult']) #turn the matrix into a pandas dataframe for easy matrix math
        #patch_adjustdf.to_csv("patch_changes.csv") ## this is here for debugging purposes. Uncomment if you want the patch adjustments to be written to a file.

        millet_df['mpatch'] = millet_df['mpatch'] = millet_df['mpatch'].where((millet_df['mpatch'] + patch_adjustdf['cult'] > maxpatch - cultiv) | (millet_df['mpatch'] + patch_adjustdf['cult'] < mpatch + cultiv), other=millet_df['mpatch'] + patch_adjustdf['cult']) # adjust the patch density column, but only if the value will stay between mpatch and maxpatch.

        millet_df['mprop'] = millet_df['mprop'].where((millet_df['mprop'] + patch_adjustdf['sel'] > 1 - currentmdiffus) | (millet_df['mprop'] + patch_adjustdf['sel'] < 0 + mselect), other=millet_df['mprop'] + patch_adjustdf['sel']) # adjust the selection coefficient column, but only if the value will stay between 1 and 0.

        #millet_df.to_csv('supposed_new_patches.csv') ## this is here for debugging purposes. Uncomment if you want the new patches to be written to a file.
        #update the patch time-series dataframes with the current year's data
        patchdens_ts[year] = millet_df.mpatch
        patchprop_ts[year] = millet_df.mprop
        ######## Okay, now update the data containers
        yr.append(year)
        hpop.append(people)
        hkcald.append((people * hkcal) - kcalneed)
        dpop.append(deer)
        mpop.append(np.sum(millet_df.mpatch)/1000.)
        dkil.append(eatdeer)
        mexp.append(eatmillet)
        mdom.append(1 - np.mean(millet_df.mprop))
        mdens.append((np.mean(millet_df.mpatch))/1000.)
    ######
    ###### Simulation has ended, write stats
    gsf = '%s%sSimulation_general_stats.%s.csv' % (os.getcwd(), os.sep, label)
    mstatsout = pd.DataFrame(data=np.array([yr, hpop, hkcald, dpop, dkil, mpop, mexp, mdom, mdens]).T, columns = ["Year","Total Human Population","Human Kcal Deficit","Total Deer Population","Number of Deer Eaten","Total Millet Population (*10^3)","Number of Millet Patches Exploited","Proportion of Domestic-Type Millet","Average Millet Patch Density (*10^3)"])      # put the main stats data in a pandas data frame for easy formatting
    mstatsout.to_csv(gsf, float_format='%.5f')
    msf1 = '%s%sSimulation_millet_patch_density_stats.%s.csv' % (os.getcwd(), os.sep, label)
    patchdens_ts.to_csv(msf1, float_format='%.5f')
    msf2 = '%s%sSimulation_millet_patch_domestic_proportion_stats.%s.csv' % (os.getcwd(), os.sep, label)
    patchprop_ts.to_csv(msf2, float_format='%.5f')
    sys.exit(0)

