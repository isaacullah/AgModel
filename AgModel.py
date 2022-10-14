#!usr/bin/python

# Model Description
############################
# This model simulates a complex hunter-gatherer band making optimal foraging decisions between a high-ranked resource and a low-ranked resource. The high-ranked resource is rich, but hard to find and proces,and potentially very scarce. The low-ranked resource is poor, but common and easy to find and process.

## Notes
#    Low-ranked resource parameterized for millet.
#    Domestic millet produces 1014 kcal/kg, yielding 1000 kg/ha from seeds dispersed at 10 kg/ha, with 176,000 seeds per kilogram (so 1.76 million plants per ha), and a return rate of about 500 kcal/hr once encountered. Assume patch size is one hectare. Data from FAO: http://www.fao.org/ag/AGP/AGPC/doc/gbase/data/pf000280.htm
#     Wild millet: Right now, just assuming everything is half as much as domestic millet.
# High ranked resource parameterized as deer, producing 1580 kcal/kg, with 100 kg yield per animal, and a return rate of abotu 10000 kcal/hr once encountered. Assuming two fawns per year and three days average search time when there are 1000 animals in the vicinity. Some of these are estimates from Bettinger 1991, and some come from USDA nutrition info for vennison.
#Note that this model assumes storage of millet, but not of deer

#Changelog:
    # v0.3 to v0.4
    # upgraded to Python 3
    # changes to GUI and interaction
    # selection is now balanced against diffusion in utilized patches.
    # diffusion is now density dependent, so that it reduces as the percentage of domestic phenotype in the ecosystem increases.
    # added docstrings to classes and functions (no functional changes)

# DO NOT EDIT BELOW THIS LINE
#########################################################################################################################################


import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import easygui as eg

class Settings(eg.EgStore):
    '''set up an Egstore class to store model settings'''
    def __init__(self, filename):  # filename is required
        '''-------------------------------------------------
        # Specify default/initial values for variables that
        # this particular application wants to remember.
        #-------------------------------------------------'''
        # HUMAN VARIABLES
        self.people = 50         ## Enter the initial number of people in the band
        self.maxpeople = 500    ## Enter the maximum human population (just to keep this in the realm of possibility, and to help set the y axis on the plot)
        self.hbirth = 0.032         ## Enter the annual human per capita birth rate
        self.hdeath = 0.03        ## Enter the annual human per capita death rate
        self.starvthresh = 0.8    ## Enter the starvation threshold (percentage of the total kcal below which people are starving, and effective reproduction goes to 0)
        self.hkcal = 547500.0 #for a 1500 kcal diet,730000.0 for a 2000kcal diet, or 1095000.0 for a 3000kcal diet    ## Enter the number of kcals per year rquired per person
        self.fhours = 4380        ## Enter the number of foraging hours available per person
        self.hgratio = 0.5        ## Enter the ratio of hunters to gatherers in the population (allocates foraging type efforts)
        # DEER VARIABLES
        self.deer = 4000         ## Enter the inital number of deer in the hunting region
        self.maxdeer = 6000     ## Enter the maximum number of deer that the region can sustain (carrying capacity) without human predation
        self.dmigrants = 10        ## Enter the number of new deer that migrate into the territory each year (keeps deer pop from being totally wiped out)
        self.dbirth = 0.06        ## Enter the annual per capit birth rate for deer
        self.ddeath = 0.02        ## Enter the annual per capita natural death rate for deer
        self.dret = 158000.0        ## Enter the return rate (number of kcals) per deer killed
        self.ddsrch = 72.0        ## Enter the density dependent search costs for deer (hours time expended per recovery of one deer at the density "ddens")
        self.ddens = 1000        ## Density of deer for which search cost "dsrch" is known
        self.dpatch = 1.0        ## Number of individual deer encountered per discovery
        self.dhndl = 16.0        ## Enter the handling costs for deer (hours handling time expended per deer once encountered)
        # MILLET VARIABLES
        self.millet = 500        ## Enter the number of millet patches in the gathering region (assume a patch is ~1ha)
        #mout = 100.0        ## Enter the viable seed yield per plant
        #mdud = .99        ## Enter the proportion of seeds that don't germinate due to predation or improper emplantation
        self.mretw = 0.0507        ## Enter the return rate (number of kcals) per wild-type millet seed
        self.mretd = 0.1014        ## Enter the return rate (number of kcals) per domestic-type millet seed
        self.mprop = 0.98        ## Enter the starting proportion of wild-type to domestic-type millet (1.0 = all wild, 0.0 = all domestic)
        self.mselect = 0.03        ## Enter the coefficient of slection (e.g., the rate of change from wild-type to domestic type)
        self.mdiffus = 0.02        ## Enter the coefficient of diffusion for millet (the rate at which selected domestic traits dissappear due to crossbreeding)
        self.msrch = 1.0        ## Enter the search costs for millet (hours expended to find one patch of millet)
        self.mpatch = 880000    ## Number of millet plants per patch at the start of the simulation (individuals encountered per discovery)
        self.maxpatch = 1760000 ## Maximum number of millet plants that can be grown per patch (a bit of a teleology, but we need a stopping point for now)
        self.cultiv = 5000 ## Number of additional millet plants to added to a patch each year due to proto cultivation of the patch. The patch reduces by the same number if not exploited.
        self.mhndlw = 0.0001        ## Enter the handling costs for wild millet (hours handling time expended per seed once encountered)
        self.mhndld = 0.00005        ## Enter the handling costs for domestic millet (hours handling time expended per seed once encountered)
        # SIMULATION CONTROLS
        self.years = 1000        ## Enter the number of years for which to run the simulation

        self.filename = filename  # this is required
        self.restore()            # restore values from the storage file if possible

#Make some custom functions for the population dynamics

def babymaker(p, n):
    '''p is the per capita birth rate, n is the population size'''
    babys = 0
    for m in range(int(n)):
        x = np.random.random()
        if x < float(p):
            babys = babys + 1
    return(babys)

def deathdealer(p, n):
    '''p is the per capita death rate, n is the population size'''
    deaths = 0
    for m in range(int(n)):
        x = np.random.random()
        if x < float(p):
            deaths = deaths + 1
    return(deaths)

#Run setup routine
# make/get the settings file
settingsFilename = eg.fileopenbox("Choose a settings file to load/save model variables from. \nIf there is no existing settings file, press 'Cancel'", "Settings", default='%s%s*.config' % (os.getcwd(), os.sep), filetypes=["*.config"])
if settingsFilename == None:
    settingsFilename = eg.filesavebox("Create a settings file to save model variables to.", "Settings", default='%s%sagmodel.config' % (os.getcwd(), os.sep), filetypes=["*.config"])
    open(settingsFilename, 'w')
settings = Settings(settingsFilename) # enact the setup
# run a dialog to see if the user wants to change anything
fieldNames = ["Inital number of people","Maximum human population","Human birth rate","Human death rate","Human starvation threshold (percentage of kcal need)","Yearly per capita kcal need","Per capita hours of work available","Ratio of hunters to gatherers in the population (allocates foraging type efforts)","Initial number of deer","Maximum number of deer","Number of deer that migrate into the territory per year","deer birth rate","Deer death rate (pre-hunting)","Kcal return from an average deer","Hours search time to find a deer","Density for which the search time is known","Number of deer per encounter","Hours of handling time per deer encountered","Number of millet patches (assume 1ha/patch)","Return rate (kcal) per wild-type millet seed","Return rate (kcal) per domestic-type millet seed","Initial proportion of wild to domestic types","Selection coeficient (percentage per year)","Diffusion coefficient (percentage per year)","Hours of search time to find a millet patch","Initial (and minimum) number of individuals per patch","Maximum number of individuals per patch","Rate at which farming increases the number of individuals in a patch","Handling time (hours) per wild millet seed","Handling time (hours) per domestic millet seed","Number of years to run the simulation"]
fieldValues = [settings.people,settings.maxpeople,settings.hbirth,settings.hdeath,settings.starvthresh,settings.hkcal,settings.fhours,settings.hgratio,settings.deer,settings.maxdeer,settings.dmigrants,settings.dbirth,settings.ddeath,settings.dret,settings.ddsrch,settings.ddens,settings.dpatch,settings.dhndl,settings.millet,settings.mretw,settings.mretd,settings.mprop,settings.mselect,settings.mdiffus,settings.msrch,settings.mpatch,settings.maxpatch,settings.cultiv,settings.mhndlw,settings.mhndld,settings.years]
title = "Model Setup"
# Massive entry dialog
fieldValues = eg.multenterbox("Enter/modify model parameters.",title, fieldNames, fieldValues)
# make sure that none of the fields was left blank
while 1:
	if fieldValues is None:
		break
	errmsg = ""
	for i in range(len(fieldNames)):
		if fieldValues[i].strip() == "":
			errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
	if errmsg == "":
		break # no problems found
	fieldValues = eg.multenterbox(errmsg, title, fieldNames, fieldValues)

### Commented out multiple individual entry dialogs in favor of one big one.
# #Do human values
# fieldValues[0:8] = eg.multenterbox("Enter/modify parameters for the forager population",title, fieldNames[0:8], fieldValues[0:8])
# # make sure that none of the fields was left blank
# while 1:
    # if fieldValues[0:8] == None: break
    # errmsg = ""
    # for i in range(len(fieldNames[0:8])):
      # if fieldValues[i].strip() == "":
        # errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    # if errmsg == "": break # no problems found
    # fieldValues[0:8] = eg.multenterbox(errmsg, title, fieldNames[0:8], fieldValues[0:8])
# #do deer values
# fieldValues[8:18] = eg.multenterbox("Enter/modify parameters for the deer population",title, fieldNames[8:18], fieldValues[8:18])
# # make sure that none of the fields was left blank
# while 1:
    # if fieldValues[8:18] == None: break
    # errmsg = ""
    # for i in range(len(fieldNames[8:18])):
      # if fieldValues[i].strip() == "":
        # errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    # if errmsg == "": break # no problems found
    # fieldValues[8:18] = eg.multenterbox(errmsg, title, fieldNames[8:18], fieldValues[8:18])
# #do millet values
# fieldValues[18:30] = eg.multenterbox("Enter/modify parameters for the forager population",title, fieldNames[18:30], fieldValues[18:30])
# # make sure that none of the fields was left blank
# while 1:
    # if fieldValues[18:30] == None: break
    # errmsg = ""
    # for i in range(len(fieldNames[18:30])):
      # if fieldValues[i].strip() == "":
        # errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    # if errmsg == "": break # no problems found
    # fieldValues[18:30] = eg.multenterbox(errmsg, title, fieldNames[18:30], fieldValues[18:30])
# #do years
# fieldValues[30] = eg.enterbox('For how many years should the simulation run?', title, fieldValues[30])
# while 1:
    # if fieldValues[30] == None: break
    # errmsg = ""
    # if fieldValues[30].strip == "":
        # errmsg = errmsg + ("This is a required field!\n")
    # if errmsg == "": break # no problems found
    # fieldValues[30] = eg.enterbox('%sFor how many years should the simulation run?' % errmsg, title, fieldValues[30])
# now, set all the new values of variables in the settings class
settings.people = int(float(fieldValues[0]))
settings.maxpeople = int(float(fieldValues[1]))
settings.hbirth = float(fieldValues[2])
settings.hdeath = float(fieldValues[3])
settings.starvthresh = float(fieldValues[4])
settings.hkcal = float(fieldValues[5])
settings.fhours = float(fieldValues[6])
settings.hgratio = float(fieldValues[7])
settings.deer = int(float(fieldValues[8]))
settings.maxdeer = int(float(fieldValues[9]))
settings.dmigrants = int(float(fieldValues[10]))
settings.dbirth = float(fieldValues[11])
settings.ddeath = float(fieldValues[12])
settings.dret = float(fieldValues[13])
settings.ddsrch = float(fieldValues[14])
settings.ddens = float(fieldValues[15])
settings.dpatch = float(fieldValues[16])
settings.dhndl = float(fieldValues[17])
settings.millet = int(float(fieldValues[18]))
settings.mretw = float(fieldValues[19])
settings.mretd = float(fieldValues[20])
settings.mprop = float(fieldValues[21])
settings.mselect = float(fieldValues[22])
settings.mdiffus = float(fieldValues[23])
settings.msrch = float(fieldValues[24])
settings.mpatch = float(fieldValues[25])
settings.maxpatch = float(fieldValues[26])
settings.cultiv = float(fieldValues[27])
settings.mhndlw = float(fieldValues[28])
settings.mhndld = float(fieldValues[29])
settings.years = int(float(fieldValues[30]))
#now write these to the settings file
settings.store()
#now set the internal simulation variables to these values
people = int(float(fieldValues[0]))
maxpeople = int(float(fieldValues[1]))
hbirth = float(fieldValues[2])
hdeath = float(fieldValues[3])
starvthresh = float(fieldValues[4])
hkcal = float(fieldValues[5])
fhours = float(fieldValues[6])
hgratio = float(fieldValues[7])
deer = int(float(fieldValues[8]))
maxdeer = int(float(fieldValues[9]))
dmigrants = int(float(fieldValues[10]))
dbirth = float(fieldValues[11])
ddeath = float(fieldValues[12])
dret = float(fieldValues[13])
ddsrch = float(fieldValues[14])
ddens = float(fieldValues[15])
dpatch = float(fieldValues[16])
dhndl = float(fieldValues[17])
millet = int(float(fieldValues[18]))
mretw = float(fieldValues[19])
mretd = float(fieldValues[20])
mprop = float(fieldValues[21])
mselect = float(fieldValues[22])
mdiffus = float(fieldValues[23])
msrch = float(fieldValues[24])
mpatch = float(fieldValues[25])
maxpatch = float(fieldValues[26])
cultiv = float(fieldValues[27])
mhndlw = float(fieldValues[28])
mhndld = float(fieldValues[29])
years = int(float(fieldValues[30]))


if __name__ == "__main__":
    ##### Setup the simulation
    milletpatches = []
    for patch in range(int(millet)): # set up a data container for our millet patches.
        milletpatches.append([mpatch, mprop]) # They will all start out the same.
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

    # Setup the plot window with 4 subplots, the axes array is 1-d
    fig = plt.figure(figsize=(15,10))
    plt.ion()
    ax1 = fig.add_subplot(411) # creates first axis, for human population amount
    plt.title('Simulation output')
    ax1.set_ylabel('People')
    ax1.axis([0, years, 0, maxpeople]) #set extents of x and y axes
    ax2 = fig.add_subplot(412, sharex=ax1) # creates second axis, will have deer pop, and number of millet patches
    ax2.axis([0, years, 0, maxdeer])
    ax2.set_ylabel('Deer')
    ax3 = ax2.twinx() # put this line on the same plot as ax2
    ax3.axis([0, years, (millet * mpatch)/1000., (millet * maxpatch)/1000.])
    ax3.set_ylabel('Millet (10^3)', color='r')
    for tl in ax3.get_yticklabels():
        tl.set_color('r')
    ax4 = fig.add_subplot(413, sharex=ax1) # creates third axis, will have number of deer eaten and number of millet patches exploited
    ax4.axis([0, years, 0, ddens/2])
    ax4.set_ylabel('Deer eaten')
    ax5 = ax4.twinx()
    ax5.axis([0, years, 0, millet])
    ax5.set_ylabel('Millet patches used', color = 'r')
    for tl in ax5.get_yticklabels():
        tl.set_color('r')
    ax6 = fig.add_subplot(414, sharex=ax1) # creates third axis, will have number of deer eaten and number of millet patches exploited
    ax6.axis([0, years, 0, 1])
    ax6.set_ylabel('% Domestic-Type Millet')
    ax7 = ax6.twinx()
    ax7.axis([0, years, mpatch/1000., (maxpatch/1000.)])
    ax7.set_ylabel('Millet Patch Density (10^3)', color = 'r')
    for tl in ax7.get_yticklabels():
        tl.set_color('r')
    ax6.set_xlabel('Years')
    p1, = ax1.plot(yr, hpop, 'k-') #Note the comma!!! Very important to have the comma!!!
    p2, = ax2.plot(yr, dpop, 'k-') #Note the comma!!! Very important to have the comma!!!
    p3, = ax3.plot(yr, mpop, 'r-') #Note the comma!!! Very important to have the comma!!!
    p4, = ax4.plot(yr, dkil, 'k-') #Note the comma!!! Very important to have the comma!!!
    p5, = ax5.plot(yr, mexp, 'r-') #Note the comma!!! Very important to have the comma!!!
    p6, = ax6.plot(yr, mdom, 'k-') #Note the comma!!! Very important to have the comma!!!
    p7, = ax7.plot(yr, mdens, 'r-') #Note the comma!!! Very important to have the comma!!!
    plt.setp( ax1.get_xticklabels(), visible=False)
    # show the plot window, pop up a command window, and wait for user input to start the simulation
    plt.show()
    msg = "Choose how to run the simulation (real time updates may significantly slow the simulation)"
    title = "Start simulation?"
    choices = ["Run with no realtime output","Run with realtime plot and terminal output.","Run with realtime terminal ouput only.","Run with realtime plot only.","Abort."]
    choice = eg.indexbox(msg, title, choices, default_choice=choices[0], cancel_choice=choices[4])
    if choice == 4:
    	sys.exit(0)
    if choice == 1 or choice == 3:
        RealTimePlotting = True  
    else:  # user chose Cancel
        RealTimePlotting = False
    if choice == 1 or choice == 2:
        RealTimeText = True
    else:
        RealTimeText= False
    ####### The simulation starts here.
    t0 = time.time() #set up a timer to see how fast we are
    print("Simulation initiated.")
    for year in range(1,years+1):        #this is the outer loop, that does things at an annual resolution, counting the years down for the simulation
        if RealTimeText: print("Year: %s" % year)
        kcalneed = people * hkcal        # find the number of kcals needed by the band this year
        htimebudget = people * fhours * hgratio        # find the hunting time budget for the band this year
        gtimebudget = people * fhours * (1/hgratio)    # find the gathering time budget for the band this year ##NOTE- excess hunting time will be used for gathering
        deer_now = deer            #set up a variable to track deer population exploitation this year
        millet_now = millet        #set up a variable to track millet patch exploitation this year
        eatmillet = 0        #set up data container to count how many millet patches we ate this year
        eatdeer = 0        #set up dat container to count how many deer we ate this year
        while kcalneed > 0:        #this is the inner loop, doing foraging within the year, until kcal need is satisfied
            if deer_now <= 0 and millet_now <= 0:
                if RealTimeText: print("ate everything!!!")
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
            #if RealTimeText: print deerscore, milletscore, kcalneed
            if deerscore >= milletscore:        #check to see whether the band should eat deer or millet at this moment
                ## eating deer, so update data containers accordingly
                if htimebudget <= 0:
                    if RealTimeText: print("Ran out of hunting time this year, hopefully there is gathering time left")
                    deerscore = 0
                    pass
                if deer_now <= 0: #if they killed all the deer, then go to millet if possible
                    if RealTimeText: print("Killed all the deer available this year, will try to make up the remainder of the diet with millet")
                    deerscore = 0.
                    pass
                else:
                    kcalneed = kcalneed - dret ## QUESTION: should this be the return for a deer minus the search/handle costs?? Or is that included in the daily dietary need (i.e., the energy expended searching and processing foodstuffs)
                    htimebudget = htimebudget - (dsrch_now + (dhndl * dpatch))
                    eatdeer = eatdeer + dpatch
                    deer_now = deer_now - dpatch
            else: ## eating millet, so update data containers accordingly
                if gtimebudget <= 0:
                    if RealTimeText: print("Ran out of gathering time this year, hopefully there is hunting time left")
                    milletscore = 0
                    pass
                elif gtimebudget <= 0 and htimebudget > 0:
                    if RealTimeText: print("Using remaining hunting time to gather millet")
                    kcalneed = kcalneed - (mret * mpatch_now)
                    htimebudget = htimebudget - msrch - (mhndl * mpatch_now)
                    eatmillet = eatmillet + 1
                    millet_now = millet_now - 1
                elif gtimebudget <=0 and htimebudget <= 0:
                    if RealTimeText: print("Not enough hunting time left to use for gathering")
                    milletscore = 0
                    pass
                else: pass
                if millet_now <= 0: #if millet is all gone, then go back to deer
                    if RealTimeText: print("Harvested all available millet this year, will try to make up the remainder of the diet with deer.")
                    milletscore = 0
                    pass
                else:
                    kcalneed = kcalneed - (mret * mpatch_now)
                    gtimebudget = gtimebudget - msrch - (mhndl * mpatch_now)
                    eatmillet = eatmillet + 1
                    millet_now = millet_now - 1
            if htimebudget <= 0 and gtimebudget <= 0:        #check if they've run out of foraging time, and stop the loop if necessary.
                if RealTimeText: print("Ran out of all foraging time for this year before gathering enough food.")
                break
            if deer <= 0 and millet <= 0:    #check if they've run out of food, and stop the loop if necessary.
                if RealTimeText: print("Ate all the deer and all the millet this year before gathering enough food.")
                break
            if deerscore <= 0 and milletscore <= 0:    #check if they've run out of food, and stop the loop if necessary.
                if RealTimeText: print("Ate all the deer and all the millet this year before gathering enough food.")
                break
        ####### Now that the band has foraged for a year, update human, deer, and millet populations, and implement selection
        if (people * hkcal) - kcalneed <= (people * hkcal * starvthresh):     #Check if they starved this year and just die deaths if so
            if RealTimeText: print("Starved a bit this year, no births will occur.")
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

        #millet_df.to_csv('supposed_new_patches.csv') ## this is here for debugging purposes. Uncomment if you want the patch adjustments to be written to a file.
        #update the patch time-series dataframes with the current year's data
        patchdens_ts[year] = millet_df.mpatch
        patchprop_ts[year] = millet_df.mprop
        ######## Okay, now update the live plot data
        yr.append(year)
        hpop.append(people)
        hkcald.append((people * hkcal) - kcalneed)
        dpop.append(deer)
        mpop.append(np.sum(millet_df.mpatch)/1000.)
        dkil.append(eatdeer)
        mexp.append(eatmillet)
        mdom.append(1 - np.mean(millet_df.mprop))
        mdens.append((np.mean(millet_df.mpatch))/1000.)
        p1.set_data(yr, hpop)
        p2.set_data(yr, dpop)
        p3.set_data(yr, mpop)
        p4.set_data(yr, dkil)
        p5.set_data(yr, mexp)
        p6.set_data(yr, mdom)
        p7.set_data(yr, mdens)
        if RealTimePlotting is True:
            fig.canvas.draw()
            fig.canvas.flush_events()
        else:
            plt.draw()
    ######
    t1 = time.time()
    print("Simulation Finished.\nTotal compute time is", round(t1-t0, 2), "seconds.")
    ###### Simulation has ended, pop up a gui box to ask if/where to save files.
    msg = "Select the stats or graphics you want to save."
    title = "Simulation Finished."
    choices = ["General Stats","Millet Patches Stats","Plot"]
    choice = eg.multchoicebox(msg, title, choices)
    if choice is None:
    	sys.exit(0)
    if "General Stats" in choice:
        gsf = eg.filesavebox("Choose a file to save the general stats to", "Save General Stats", default='%s%sSimulation_general_stats.csv' % (os.getcwd(), os.sep), filetypes=["*.csv", "Comma separated ASCII text files"])
        mstatsout = pd.DataFrame(data=np.array([yr, hpop, hkcald, dpop, dkil, mpop, mexp, mdom, mdens]).T, columns = ["Year","Total Human Population","Human Kcal Deficit","Total Deer Population","Number of Deer Eaten","Total Millet Population (*10^3)","Number of Millet Patches Exploited","Proportion of Domestic-Type Millet","Average Millet Patch Density (*10^3)"])      # put the main stats data in a pandas data frame for easy formatting
        if gsf == '': # did the user press cancel, or not enter a file name? If so, then pass, otherwise, write the file.
            pass
        else:
            mstatsout.to_csv(gsf, float_format='%.5f')
    else:
        pass
    if "Millet Patches Stats" in choice:
        msf1 = eg.filesavebox("Choose a file to save the millet patches density stats to", "Save Millet Patch Stats", default='%s%sSimulation_millet_patch_density_stats.csv' % (os.getcwd(), os.sep), filetypes=["*.csv"])
        if msf1 == '':
            pass
        else:
            patchdens_ts.to_csv(msf1, float_format='%.5f')
        msf2 = eg.filesavebox("Choose a file to save the millet patches domesticated proportion stats to", "Save Millet Patch Stats", default='%s%sSimulation_millet_patch_domestic_proportion_stats.csv' % (os.getcwd(), os.sep), filetypes=["*.csv"])
        if msf2 == '':
            pass
        else:
            patchprop_ts.to_csv(msf2, float_format='%.5f')
    else:
        pass
    if "Plot" in choice:
        pf = eg.filesavebox("Choose a file to save the plot to. \nPlease write the correct file extension for the filetype that you want.", "Save Plot", default='%s%sSimulation_plot.svg' % (os.getcwd(), os.sep), filetypes=["*.svg", "*.png", "*.tif"])
        if pf == '':
            pass
        else:
            plt.savefig(pf, format = pf.split('.')[1], edgecolor = "black")
    else:
        pass
    eg.msgbox(msg='Close Simulation', title='Exit', ok_button='OK')
    sys.exit(0)

