#!usr/bin/python

# Model Description
############################
# This model simulates a complex hunter-gatherer band making optimal foraging decisions between a high-ranked resource and a low-ranked resource. The high-ranked resource is rich, but hard to find and process,and potentially very scarce. The low-ranked resource is poor, but common and easy to find and process.

## Current Version: v0.6

#Changelog:

    ### Proposed Changes for next version
    #   Introduce SeedToYieldRatio, and use it to replace the variables for initial and maximum Kernel yields per patch to be initial and maximum SeedToYieldRatio
    #   Tie the SelectionCoefficient to also increase the SeedToYieldRatio over time.
    #   Add a WildSeedingRate and CultivationSeedingRate (number of kernels/ha) and remove CerealCultivationDensity
    #   Allow for surplus and storage
    #   Allow birth rate and death rate to be positively affected by surplus
    #   Increase diversity of alternative food resources (more than just one prey or plant resource)

    # v0.5 to v0.6
    # Removed HunterGathererRatio (allows this to be an emergent property)
    # Added Gaussian filter to diet breadth logic
    # Added randomization of prey encounter number
    # Added Gaussian filter to coevolutionary selection and diffusion rates

    # v0.4 to v0.5
    # Updated variable names for readability

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
        self.People = 50         ## Enter the initial number of people in the band
        self.MaximumPeople = 3000    ## Enter the maximum human population (just to keep this in the realm of possibility, and to help set the y axis on the plot)
        self.HumanBirthRate = 0.032         ## Enter the annual human per capita birth rate
        self.HumanDeathRate = 0.03        ## Enter the annual human per capita death rate
        self.HumanBirthDeathFilter = 0.005 ## Width of the Gaussian randomizing filter for human birth and death rates
        self.StarvationThreshold = 0.8    ## Enter the starvation threshold (percentage of the total kcal below which people are starving, and effective reproduction goes to 0)
        self.HumanKcal = 912500.0    ## Enter the number of kcals per year required per person
                                    # 547500 for a 1500 kcal diet,730000.0 for a 2000kcal diet, 912500 for a 2500kcal diet, or 1095000.0 for a 3000kcal diet
        self.ForagingHours = 4380       ## Enter the number of foraging hours available per person
                                        # 4380 for 12hrs/day
        self.ForagingUncertainty = 0.1        ## Width of the Gaussian randomizing filter that is applied to foraging payoff numbers in the forager's Diet Breadth decision algorithm
        # PREY VARIABLES
        self.Prey = 200         ## Enter the initial number of Prey in the hunting region
        self.MaxPrey = 500     ## Enter the maximum number of Prey that the region can sustain (carrying capacity) without human predation
        self.MaxPreyMigrants = 0        ## Enter the maximum number of new Prey that migrate into the territory each year (keeps Prey pop from being totally wiped out)
        self.PreyBirthRate = 0.06        ## Enter the annual per capita birth rate for Prey
        self.PreyDeathRate = 0.04        ## Enter the annual per capita natural death rate for Prey
        self.PreyBirthDeathFilter = 0.005 ## Width of the Gaussian randomizing filter for prey birth and death rates
        self.PreyReturns = 200000.0        ## Enter the return rate (number of kcals) per Prey killed
        self.PreySearchCost = 72.0        ## Enter the density dependent search costs for Prey (hours time expended per recovery of one Prey at the density "PreyDensity")
        self.PreyDensity = 1000        ## Density of Prey for which search cost prey search costs are known
        self.MaxPreyEncountered = 4.0        ## Maximum number of individual Prey encountered per discovery
        self.MinPreyEncountered = 1.0        ## Minimum number of individual Prey encountered per discovery
        self.PreyHandlingCost = 16.0        ## Enter the handling costs for Prey (hours handling time expended once encountered)
        # CEREAL VARIABLES
        self.Cereal = 100        ## Enter the number of Cereal patches in the gathering region (assume a patch is ~1ha)
        self.WildCerealReturns = 0.05        ## Enter the return rate (number of kcals) per wild-type Cereal seed
        self.DomesticatedCerealReturns = 0.1        ## Enter the return rate (number of kcals) per domestic-type Cereal seed
        self.WildToDomesticatedProportion = 0.98        ## Enter the starting proportion of wild-type to domestic-type Cereal (1.0 = all wild, 0.0 = all domestic)
        self.CerealSelectionRate = 0.03        ## Enter the coefficient of selection (e.g., the rate of change from wild-type to domestic type)
        self.CerealDiffusionRate = 0.02        ## Enter the coefficient of diffusion for Cereal (the rate at which selected domestic traits disappear due to crossbreeding)
        self.SelectionDiffusionFilter = 0.001   ## Enter the width of the Gaussian filter applied to selection and diffusion rates.
        self.CerealSearchCosts = 1.0        ## Enter the search costs for Cereal (hours expended to find one patch of Cereal)
        self.CerealDensity = 10000000    ## Number of Cereal kernels that are harvested per patch at the start of the simulation
        self.MaxCerealDensity = 100000000 ## Maximum number of Cereal kernels that can be harvest per patch (a bit of a teleology, but we need a stopping point)
        self.CerealCultivationDensity = 1000000 ## Number of additional Cereal kernels that can be harvested from a patch each year due to proto-cultivation of the patch (up to maximum density). The patch yield reduces by the same number if not exploited (down to minimum)
        self.WildCerealHandlingCost = 0.0001        ## Enter the handling costs for wild Cereal (hours handling time expended per seed once encountered)
        self.DomesticatedCerealHandlingCost = 0.00001        ## Enter the handling costs for domestic Cereal (hours handling time expended per seed once encountered)
        # SIMULATION CONTROLS
        self.Years = 3000        ## Enter the number of years for which to run the simulation

        self.filename = filename  # this is required

#Make some custom functions for the population dynamics

def babymaker(p, f, n):
    '''p is the per capita birth rate, f is the width of the Gaussian filter, n is the population size'''
    babys = np.round(np.random.normal(p,f)*n)
    return(babys)

def deathdealer(p, f, n):
    '''p is the per capita death rate, f is the width of the Gaussian filter, n is the population size'''
    deaths = np.round(np.random.normal(p,f)*n)
    return(deaths)

#Run setup routine
# make/get the settings file
settingsFilename = eg.fileopenbox("Choose a settings file to load/save model variables from. If there is no existing settings file, press 'Cancel'", "Settings", default='%s%s*.config' % (os.getcwd(), os.sep), filetypes=["*.config"])
if settingsFilename == None:
    settingsFilename = eg.filesavebox("Create a settings file to save model variables to.", "Settings", default='%s%sagmodel.config' % (os.getcwd(), os.sep), filetypes=["*.config"])
    open(settingsFilename, 'w')
    settings = Settings(settingsFilename) # enact the setup
else:
    settings = Settings(settingsFilename) # enact the setup
    settings.restore() # restore values
# run a dialog to see if the user wants to change anything
fieldNames = ["Initial number of people",
            "Maximum human population",
            "Human birth rate",
            "Human death rate",
            "Width of the Gaussian randomizing filter for human birth and death rates",
            "Human starvation threshold (percentage of kcal need)",
            "Yearly per capita kcal need",
            "Per capita hours of work available",
            "Width of the Gaussian randomizing filter for foraging returns",
            "Initial number of prey",
            "Maximum number of prey",
            "Maximum number of prey that migrate into the territory per year",
            "Prey birth rate",
            "Intrinsic prey death rate (without human hunting)",
            "Width of the Gaussian randomizing filter for prey birth and death rates",
            "Kcal return from an average prey",
            "Hours search time to find a prey",
            "Density for which the prey search time is known",
            "Maximum number of prey per encounter",
            "Minimum number of prey per encounter",
            "Hours of handling time per encounter",
            "Number of cereal patches (patch size is 1ha)",
            "Return rate (kcal) per wild-type cereal seed",
            "Return rate (kcal) per domestic-type cereal seed",
            "Initial proportion of wild to domestic types",
            "Selection coefficient (percentage per year)",
            "Diffusion coefficient (percentage per year)",
            "Width of the Gaussian filter applied to selection and diffusion rate",
            "Hours of search time to find a cereal patch",
            "Initial (and minimum) cereal kernel yield per patch",
            "Maximum cereal kernel yield per patch",
            "Rate at which proto-cultivation increases the kernel yield in a patch",
            "Handling time (hours) per wild cereal seed",
            "Handling time (hours) per domestic cereal seed",
            "Number of years to run the simulation"]
fieldValues = [settings.People,
            settings.MaximumPeople,
            settings.HumanBirthRate,
            settings.HumanDeathRate,
            settings.HumanBirthDeathFilter,
            settings.StarvationThreshold,
            settings.HumanKcal,
            settings.ForagingHours,
            settings.ForagingUncertainty,
            settings.Prey,
            settings.MaxPrey,
            settings.MaxPreyMigrants,
            settings.PreyBirthRate,
            settings.PreyDeathRate,
            settings.PreyBirthDeathFilter,
            settings.PreyReturns,
            settings.PreySearchCost,
            settings.PreyDensity,
            settings.MaxPreyEncountered,
            settings.MinPreyEncountered,
            settings.PreyHandlingCost,
            settings.Cereal,
            settings.WildCerealReturns,
            settings.DomesticatedCerealReturns,
            settings.WildToDomesticatedProportion,
            settings.CerealSelectionRate,
            settings.CerealDiffusionRate,
            settings.SelectionDiffusionFilter,
            settings.CerealSearchCosts,
            settings.CerealDensity,
            settings.MaxCerealDensity,
            settings.CerealCultivationDensity,
            settings.WildCerealHandlingCost,
            settings.DomesticatedCerealHandlingCost,
            settings.Years]
title = "Model Setup, 1/2"
# First half of entry dialog
fieldValues[0:21] = eg.multenterbox("Enter/modify model parameters.",title, fieldNames[0:21], fieldValues[0:21])
# make sure that none of the fields was left blank
while 1:
    if fieldValues[0:21] is None:
        break
    errmsg = ""
    for i in range(len(fieldNames[0:21])):
        if fieldValues[i].strip() == "":
            errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    if errmsg == "":
        break # no problems found
    fieldValues[0:21] = eg.multenterbox(errmsg, title, fieldNames[0:21], fieldValues[0:21])
#Second half of entry dialog
title = "Model Setup, 2/2"
fieldValues[21:36] = eg.multenterbox("Enter/modify model parameters.",title, fieldNames[21:36], fieldValues[21:36])
# make sure that none of the fields was left blank
while 1:
    if fieldValues[21:36] is None:
        break
    errmsg = ""
    for i in range(len(fieldNames[21:36])):
        if fieldValues[i].strip() == "":
            errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    if errmsg == "":
        break # no problems found
    fieldValues[21:36] = eg.multenterbox(errmsg, title, fieldNames[21:36], fieldValues[21:36])
# now, set all the new values of variables in the settings class
settings.People = int(float(fieldValues[0]))
settings.MaximumPeople = int(float(fieldValues[1]))
settings.HumanBirthRate = float(fieldValues[2])
settings.HumanDeathRate = float(fieldValues[3])
settings.HumanBirthDeathFilter = float(fieldValues[4])   ###############
settings.StarvationThreshold = float(fieldValues[5])
settings.HumanKcal = float(fieldValues[6])
settings.ForagingHours = float(fieldValues[7])
settings.ForagingUncertainty = float(fieldValues[8])
settings.Prey = int(float(fieldValues[9]))
settings.MaxPrey = int(float(fieldValues[10]))
settings.MaxPreyMigrants = int(float(fieldValues[11]))
settings.PreyBirthRate = float(fieldValues[12])
settings.PreyDeathRate = float(fieldValues[13])
settings.PreyBirthDeathFilter = float(fieldValues[14]) ###############
settings.PreyReturns = float(fieldValues[15])
settings.PreySearchCost = float(fieldValues[16])
settings.PreyDensity = float(fieldValues[17])
settings.MaxPreyEncountered = float(fieldValues[18])
settings.MinPreyEncountered = float(fieldValues[19])
settings.PreyHandlingCost = float(fieldValues[20])
settings.Cereal = int(float(fieldValues[21]))
settings.WildCerealReturns = float(fieldValues[22])
settings.DomesticatedCerealReturns = float(fieldValues[23])
settings.WildToDomesticatedProportion = float(fieldValues[24])
settings.CerealSelectionRate = float(fieldValues[25])
settings.CerealDiffusionRate = float(fieldValues[26])
settings.SelectionDiffusionFilter = float(fieldValues[27])
settings.CerealSearchCosts = float(fieldValues[28])
settings.CerealDensity = float(fieldValues[29])
settings.MaxCerealDensity = float(fieldValues[30])
settings.CerealCultivationDensity = float(fieldValues[31])
settings.WildCerealHandlingCost = float(fieldValues[32])
settings.DomesticatedCerealHandlingCost = float(fieldValues[33])
settings.Years = int(float(fieldValues[34]))
#now write these to the settings file
settings.store()
#now set the internal simulation variables to these values
People = int(float(fieldValues[0]))
MaximumPeople = int(float(fieldValues[1]))
HumanBirthRate = float(fieldValues[2])
HumanDeathRate = float(fieldValues[3])
HumanBirthDeathFilter = float(fieldValues[4])   ###############
StarvationThreshold = float(fieldValues[5])
HumanKcal = float(fieldValues[6])
ForagingHours = float(fieldValues[7])
ForagingUncertainty = float(fieldValues[8])
Prey = int(float(fieldValues[9]))
MaxPrey = int(float(fieldValues[10]))
MaxPreyMigrants = int(float(fieldValues[11]))
PreyBirthRate = float(fieldValues[12])
PreyDeathRate = float(fieldValues[13])
PreyBirthDeathFilter = float(fieldValues[14]) ###############
PreyReturns = float(fieldValues[15])
PreySearchCost = float(fieldValues[16])
PreyDensity = float(fieldValues[17])
MaxPreyEncountered = float(fieldValues[18])
MinPreyEncountered = float(fieldValues[19])
PreyHandlingCost = float(fieldValues[20])
Cereal = int(float(fieldValues[21]))
WildCerealReturns = float(fieldValues[22])
DomesticatedCerealReturns = float(fieldValues[23])
WildToDomesticatedProportion = float(fieldValues[24])
CerealSelectionRate = float(fieldValues[25])
CerealDiffusionRate = float(fieldValues[26])
SelectionDiffusionFilter = float(fieldValues[27])
CerealSearchCosts = float(fieldValues[28])
CerealDensity = float(fieldValues[29])
MaxCerealDensity = float(fieldValues[30])
CerealCultivationDensity = float(fieldValues[31])
WildCerealHandlingCost = float(fieldValues[32])
DomesticatedCerealHandlingCost = float(fieldValues[33])
Years = int(float(fieldValues[34]))


if __name__ == "__main__":
    ##### Get user input for displays and other runtime preferences
    msg = "Choose how to run the simulation -- terminal and plot output may significantly slow the run time."
    title = "Start simulation?"
    choices = ["Run with no output","Run with terminal output.","Run with plot and terminal output.","Abort."]
    choice = eg.indexbox(msg, title, choices, default_choice=choices[0], cancel_choice=choices[3])
    if choice == 3:
        sys.exit(0)
    if choice == 2:
        RealTimePlotting = True
    else:  # user chose Cancel
        RealTimePlotting = False
    if choice == 1 or choice == 2:
        RealTimeText = True
    else:
        RealTimeText= False
    ##### Setup the simulation
    Cerealpatches = []
    for patch in range(int(Cereal)): # set up a data container for our Cereal patches.
        Cerealpatches.append([CerealDensity, WildToDomesticatedProportion]) # They will all start out the same.
    Cereal_df = pd.DataFrame(Cerealpatches, columns=['CerealDensity','WildToDomesticatedProportion']) # turn this data container into a pandas dataframe for more efficient math and indexing
    patchdens_ts = pd.DataFrame(index=list(range(1,int(Cereal+1))), columns=list(range(Years+1))) # set up a blank pandas dataframe to catch patch density timeseries stats for possible output
    patchprop_ts = pd.DataFrame(index=list(range(1,int(Cereal+1))), columns=list(range(Years+1))) # set up a blank pandas dataframe to catch patch domestic proportion timeseries stats for possible output
    patchdens_ts[0] = Cereal_df.CerealDensity # update with year 0 data
    patchprop_ts[0] = Cereal_df.WildToDomesticatedProportion # update with year 0 data
    # set up some individual data containers for the output stats and plots
    yr = [0]
    HumPop = [People]
    HumanKcalPrey = [0]
    PreyPop = [Prey]
    CerealPop = [(Cereal * CerealDensity)/1000.]
    PreyKilled = [0]
    CerealExploited = [0]
    ProportionDomesticated = [1 - WildToDomesticatedProportion]
    AverageCerealDensity = [CerealDensity/1000]

    # Setup the plot window with 4 subplots, the axes array is 1-d
    fig = plt.figure(figsize=(15,10))
    plt.ion()
    ax1 = fig.add_subplot(411) # creates first axis, for human population amount
    plt.title('Simulation output')
    ax1.set_ylabel('People')
    ax1.axis([0, Years, 0, MaximumPeople]) #set extents of x and y axes
    ax2 = fig.add_subplot(412, sharex=ax1) # creates second axis, will have Prey pop, and number of Cereal patches
    ax2.axis([0, Years, 0, MaxPrey])
    ax2.set_ylabel('Prey animals')
    ax3 = ax2.twinx() # put this line on the same plot as ax2
    ax3.axis([0, Years, (Cereal * CerealDensity)/1000., (Cereal * MaxCerealDensity)/1000.])
    ax3.set_ylabel('Cereal (10^3)', color='r')
    for tl in ax3.get_yticklabels():
        tl.set_color('r')
    ax4 = fig.add_subplot(413, sharex=ax1) # creates third axis, will have number of Prey eaten and number of Cereal patches exploited
    ax4.axis([0, Years, 0, PreyDensity/2])
    ax4.set_ylabel('Prey animals eaten')
    ax5 = ax4.twinx()
    ax5.axis([0, Years, 0, Cereal])
    ax5.set_ylabel('Cereal patches used', color = 'r')
    for tl in ax5.get_yticklabels():
        tl.set_color('r')
    ax6 = fig.add_subplot(414, sharex=ax1) # creates third axis, will have number of Prey eaten and number of Cereal patches exploited
    ax6.axis([0, Years, 0, 1])
    ax6.set_ylabel('% Domestic-Type Cereal')
    ax7 = ax6.twinx()
    ax7.axis([0, Years, CerealDensity/1000., (MaxCerealDensity/1000.)])
    ax7.set_ylabel('Cereal Patch Density (10^3)', color = 'r')
    for tl in ax7.get_yticklabels():
        tl.set_color('r')
    ax6.set_xlabel('Years')
    p1, = ax1.plot(yr, HumPop, 'k-') #Note the comma!!! Very important to have the comma!!!
    p2, = ax2.plot(yr, PreyPop, 'k-') #Note the comma!!! Very important to have the comma!!!
    p3, = ax3.plot(yr, CerealPop, 'r-') #Note the comma!!! Very important to have the comma!!!
    p4, = ax4.plot(yr, PreyKilled, 'k-') #Note the comma!!! Very important to have the comma!!!
    p5, = ax5.plot(yr, CerealExploited, 'r-') #Note the comma!!! Very important to have the comma!!!
    p6, = ax6.plot(yr, ProportionDomesticated, 'k-') #Note the comma!!! Very important to have the comma!!!
    p7, = ax7.plot(yr, AverageCerealDensity, 'r-') #Note the comma!!! Very important to have the comma!!!
    plt.setp( ax1.get_xticklabels(), visible=False)
    if RealTimePlotting is True:
        # show the plot window
        plt.show()
    else:
        pass
    ####### The simulation starts here.
    t0 = time.time() #set up a timer to see how fast we are
    print("Simulation Initiated, please stand by...")
    for year in range(1,Years+1):        #this is the outer loop, that does things at an annual resolution, counting the years down for the simulation
        if RealTimeText: print("Year: %s Human Population: %s" % (year, People))
        kcalneed = People * HumanKcal        # find the number of kcals needed by the band this year
        timebudget = People * ForagingHours       # find the time budget for the band this year
        Prey_now = Prey            #set up a variable to track Prey population exploitation this year
        Cereal_now = Cereal        #set up a variable to track Cereal patch exploitation this year
        eatCereal = 0        #set up data container to count how many Cereal patches we ate this year
        eatPrey = 0        #set up data container to count how many Prey we ate this year
        while kcalneed > 0:        #this is the inner loop, doing foraging within the year, until kcal need is satisfied
            if Prey_now <= 0 and Cereal_now <= 0:
                if RealTimeText: print("ate everything!!!")
                break
            #first calculate info about the current state of Cereal
            WildToDomesticatedProportion_now = np.mean(Cereal_df.WildToDomesticatedProportion[0:Cereal_now]) #Note that we are taking the mean proportion across all remaining Cereal patches in the data array.
            CerealDensity_now = np.mean(Cereal_df.CerealDensity[0:Cereal_now]) #Note that we are taking the mean number of individuals per patch across all remaining patches in the Cereal data array. Note that we are reading off of the right end of the array list.
            CerealReturns = (WildCerealReturns * WildToDomesticatedProportion_now) + (DomesticatedCerealReturns * (1 - WildToDomesticatedProportion_now))        #determine the actual kcal return for Cereal, based on the proportion of wild to domesticated.
            CombinedCerealHandlingCost = (WildCerealHandlingCost * WildToDomesticatedProportion_now) + (DomesticatedCerealHandlingCost * (1 - WildToDomesticatedProportion_now))    #determine the actual handling time for Cereal, based on the proportion of wild to domesticated.
            if Prey_now <= 0:
                Preyscore = 0
            else:
                PreySearchCost_Now = PreySearchCost / (Prey_now / PreyDensity)        #find the actual search time for the amount of Prey at this time
                if MinPreyEncountered >= MaxPreyEncountered:
                    PreyEncountered_Now = MinPreyEncountered
                else:
                    PreyEncountered_Now = np.random.randint(MinPreyEncountered, MaxPreyEncountered)     # find how many prey are encountered at this time
                Preyscore = PreyReturns / (PreySearchCost_Now + PreyHandlingCost)    #find the current return rate (kcal/hr) for Prey.
            if Cereal_now <= 0:
                Cerealscore = 0
            else:
                Cerealscore = (CerealReturns * CerealDensity_now ) / (CerealSearchCosts + (CombinedCerealHandlingCost *  CerealDensity_now))        #find the current return rate (kcal/hr for Cereal.
            if np.random.normal(Preyscore, Preyscore * ForagingUncertainty) > np.random.normal(Cerealscore, Cerealscore * ForagingUncertainty): # Hunting prey is more profitable
                if timebudget <= 0:
                    if RealTimeText: print("Ran out of labor time this year")
                    Preyscore = 0
                    pass
                if Prey_now <= 0: #if they killed all the Prey, then go to Cereal if possible
                    if RealTimeText: print("Killed all the Prey available this year, will try to make up the remainder of the diet with Cereal")
                    Preyscore = 0.
                    pass
                else:
                    kcalneed = kcalneed - PreyReturns ## QUESTION: should this be the return for a Prey minus the search/handle costs?? Or is that included in the daily dietary need (i.e., the energy expended searching and processing foodstuffs)
                    timebudget = timebudget - (PreySearchCost_Now + (PreyHandlingCost * PreyEncountered_Now))
                    eatPrey = eatPrey + PreyEncountered_Now
                    Prey_now = Prey_now - PreyEncountered_Now
            elif np.random.normal(Preyscore, Preyscore * ForagingUncertainty) > np.random.normal(Cerealscore, Cerealscore * ForagingUncertainty): # Harvesting cereal is more profitable
                if timebudget <= 0:
                    if RealTimeText: print("Ran out of labor time this year")
                    Cerealscore = 0
                    pass
                if Cereal_now <= 0: #if Cereal is all gone, then go back to Prey
                    if RealTimeText: print("Harvested all available Cereal this year, will try to make up the remainder of the diet with Prey.")
                    Cerealscore = 0
                    pass
                else:
                    kcalneed = kcalneed - (CerealReturns * CerealDensity_now)
                    timebudget = timebudget - CerealSearchCosts - (CombinedCerealHandlingCost * CerealDensity_now)
                    eatCereal = eatCereal + 1
                    Cereal_now = Cereal_now - 1
            else: # both equally profitable, so randomly choose hunting or harvesting
                if np.random.randint(0,1) == 1:
                    if timebudget <= 0:
                        if RealTimeText: print("Ran out of labor time this year")
                        Preyscore = 0
                        pass
                    if Prey_now <= 0: #if they killed all the Prey, then go to Cereal if possible
                        if RealTimeText: print("Killed all the Prey available this year, will try to make up the remainder of the diet with Cereal")
                        Preyscore = 0.
                        pass
                    else:
                        kcalneed = kcalneed - PreyReturns ## QUESTION: should this be the return for a Prey minus the search/handle costs?? Or is that included in the daily dietary need (i.e., the energy expended searching and processing foodstuffs)
                        timebudget = timebudget - (PreySearchCost_Now + PreyHandlingCost)
                        eatPrey = eatPrey + PreyEncountered_Now
                        Prey_now = Prey_now - PreyEncountered_Now
                else:
                    if timebudget <= 0:
                        if RealTimeText: print("Ran out of labor time this year")
                        Cerealscore = 0
                        pass
                    if Cereal_now <= 0: #if Cereal is all gone, then go back to Prey
                        if RealTimeText: print("Harvested all available Cereal this year, will try to make up the remainder of the diet with Prey.")
                        Cerealscore = 0
                        pass
                    else:
                        kcalneed = kcalneed - (CerealReturns * CerealDensity_now)
                        timebudget = timebudget - CerealSearchCosts - (CombinedCerealHandlingCost * CerealDensity_now)
                        eatCereal = eatCereal + 1
                        Cereal_now = Cereal_now - 1
            if timebudget <= 0:        #check if they've run out of foraging time, and stop the loop if necessary.
                if RealTimeText: print("Ran out of all foraging time for this year before gathering enough food.")
                break
            if Prey <= 0 and Cereal <= 0:    #check if they've run out of food, and stop the loop if necessary.
                if RealTimeText: print("Ate all the Prey and all the Cereal this year before gathering enough food.")
                break
            if Preyscore <= 0 and Cerealscore <= 0:    #check if they've run out of food, and stop the loop if necessary.
                if RealTimeText: print("Ate all the Prey and all the Cereal this year before gathering enough food.")
                break
        ####### Now that the band has foraged for a year, update human, Prey, and Cereal populations, and implement selection
        if (People * HumanKcal) - kcalneed <= (People * HumanKcal * StarvationThreshold):     #Check if they starved this year and just die deaths if so
            if RealTimeText: print("Starvation occurred.")
            People = People - deathdealer(HumanDeathRate*2, HumanBirthDeathFilter, People)
        else: #otherwise, balance births and deaths, and adjust the population accordingly
            People = People + babymaker(HumanBirthRate, HumanBirthDeathFilter, People) - deathdealer(HumanDeathRate, HumanBirthDeathFilter, People)
        if MaxPreyMigrants == 0:
            PreyMigrantsNow = 0
        else:
            PreyMigrantsNow = np.random.randint(0, MaxPreyMigrants)
        Prey = Prey_now + babymaker(PreyBirthRate, PreyBirthDeathFilter, Prey_now) - deathdealer(PreyDeathRate, PreyBirthDeathFilter, Prey_now) + PreyMigrantsNow #Adjust the Prey population by calculating the balance of natural births and deaths on the hunted population, and then add the migrants population
        if People > MaximumPeople: People = MaximumPeople # don't allow human pop to exceed the limit we set
        if Prey > MaxPrey: Prey = MaxPrey # don't allow Prey pop to exceed natural carrying capacity
        #This part is a bit complicated. We are adjusting the proportions of wild to domestic Cereal in JUST the Cereal patches that were exploited this year. We are also adjusting the density of individuals in those patches. This is the effect of the "artificial selection" exhibited by humans while exploiting those patches. At the same time, we are implementing a "diffusion" of wild-type characteristics back to all the patches. If they are used, selection might outweigh diffusion. If they aren't being used, then just diffusion occurs. In this version of the model, diffusion is density dependent, and is adjusted by (lat year's) the proportion of domestic to non-domestic Cereals left in the population.
        patch_adjust = [] # make a matrix to do the selection/diffusion on the individual patches based on if they got used or not.
        currentCerealDiffusionRate = np.random.normal(CerealDiffusionRate, (CerealDiffusionRate*SelectionDiffusionFilter)) * (1 - ProportionDomesticated[-1])
        currentCerealSelectionRate = np.random.normal(CerealSelectionRate, (CerealSelectionRate*SelectionDiffusionFilter))
        for x in range(1,int(Cereal+1)):
            if x < eatCereal:
                patch_adjust.append([currentCerealDiffusionRate-currentCerealSelectionRate, CerealCultivationDensity])
            else:
                patch_adjust.append([currentCerealDiffusionRate, -CerealCultivationDensity])
        patch_adjustdf = pd.DataFrame(patch_adjust, columns=['sel', 'cult']) #turn the matrix into a pandas dataframe for easy matrix math
        #patch_adjustdf.to_csv("patch_changes.csv") ## this is here for debugging purposes. Uncomment if you want the patch adjustments to be written to a file.

        Cereal_df['CerealDensity'] = Cereal_df['CerealDensity'] = Cereal_df['CerealDensity'].where((Cereal_df['CerealDensity'] + patch_adjustdf['cult'] > MaxCerealDensity - CerealCultivationDensity) | (Cereal_df['CerealDensity'] + patch_adjustdf['cult'] < CerealDensity + CerealCultivationDensity), other=Cereal_df['CerealDensity'] + patch_adjustdf['cult']) # adjust the patch density column, but only if the value will stay between CerealDensity and MaxCerealDensity.

        Cereal_df['WildToDomesticatedProportion'] = Cereal_df['WildToDomesticatedProportion'].where((Cereal_df['WildToDomesticatedProportion'] + patch_adjustdf['sel'] > 1 - currentCerealDiffusionRate) | (Cereal_df['WildToDomesticatedProportion'] + patch_adjustdf['sel'] < 0 + currentCerealSelectionRate), other=Cereal_df['WildToDomesticatedProportion'] + patch_adjustdf['sel']) # adjust the selection coefficient column, but only if the value will stay between 1 and 0.

        #Cereal_df.to_csv('supposed_new_patches.csv') ## this is here for debugging purposes. Uncomment if you want the patch adjustments to be written to a file.
        #update the patch time-series dataframes with the current year's data
        patchdens_ts[year] = Cereal_df.CerealDensity
        patchprop_ts[year] = Cereal_df.WildToDomesticatedProportion
        ######## Okay, now update the live plot data
        yr.append(year)
        HumPop.append(People)
        HumanKcalPrey.append((People * HumanKcal) - kcalneed)
        PreyPop.append(Prey)
        CerealPop.append(np.sum(Cereal_df.CerealDensity)/1000.)
        PreyKilled.append(eatPrey)
        CerealExploited.append(eatCereal)
        ProportionDomesticated.append(1 - np.mean(Cereal_df.WildToDomesticatedProportion))
        AverageCerealDensity.append((np.mean(Cereal_df.CerealDensity))/1000.)
        p1.set_data(yr, HumPop)
        p2.set_data(yr, PreyPop)
        p3.set_data(yr, CerealPop)
        p4.set_data(yr, PreyKilled)
        p5.set_data(yr, CerealExploited)
        p6.set_data(yr, ProportionDomesticated)
        p7.set_data(yr, AverageCerealDensity)
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
    choices = ["General Stats","Cereal Patches Stats","Plot"]
    choice = eg.multchoicebox(msg, title, choices)
    if choice is None:
        sys.exit(0)
    if "General Stats" in choice:
        GeneralStatsFile = eg.filesavebox("Choose a file to save the general stats to", "Save General Stats", default='%s%sSimulation_general_stats.csv' % (os.getcwd(), os.sep), filetypes=["*.csv", "Comma separated ASCII text files"])
        statsout = pd.DataFrame(data=np.array([yr, HumPop, HumanKcalPrey, PreyPop, PreyKilled, CerealPop, CerealExploited, ProportionDomesticated, AverageCerealDensity]).T, columns = ["Year","Total Human Population","Human Kcal Deficit","Total Prey Animals Population","Number of Prey Animals Eaten","Total Cereal Population (*10^3)","Number of Cereal Patches Exploited","Proportion of Domestic-Type Cereal","Average Cereal Patch Density (*10^3)"])      # put the main stats data in a pandas data frame for easy formatting
        if GeneralStatsFile == '': # did the user press cancel, or not enter a file name? If so, then pass, otherwise, write the file.
            pass
        else:
            statsout.to_csv(GeneralStatsFile, float_format='%.5f')
    else:
        pass
    if "Cereal Patches Stats" in choice:
        CerealDensityStatsFile = eg.filesavebox("Choose a file to save the Cereal patches density stats to", "Save Cereal Patch Stats", default='%s%sSimulation_Cereal_patch_density_stats.csv' % (os.getcwd(), os.sep), filetypes=["*.csv"])
        if CerealDensityStatsFile == '':
            pass
        else:
            patchdens_ts.to_csv(CerealDensityStatsFile, float_format='%.5f')
        CerealProportionStatsFile = eg.filesavebox("Choose a file to save the Cereal patches domesticated proportion stats to", "Save Cereal Patch Stats", default='%s%sSimulation_Cereal_patch_domestic_proportion_stats.csv' % (os.getcwd(), os.sep), filetypes=["*.csv"])
        if CerealProportionStatsFile == '':
            pass
        else:
            patchprop_ts.to_csv(CerealProportionStatsFile, float_format='%.5f')
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
    sys.exit(0)

