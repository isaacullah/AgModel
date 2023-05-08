#!usr/bin/python

# Model Description
############################
# This model simulates a complex hunter-gatherer band making optimal foraging decisions between a high-ranked resource and a low-ranked resource. The high-ranked resource is rich, but hard to find and proces,and potentially very scarce. The low-ranked resource is poor, but common and easy to find and process.
# !! THIS VERSION RUNS HEADLESS (NO GUI), AND CAN BE LOOPED BY AN EXTERNAL PROGRAM !!

## Current Version: v0.6

#Changelog:

    ### Proposed Changes for next version
    #   Introduce SeedToYieldRatio, and use it to replace the variables for initial and maximum Kernel yields per patch to be initial and maximum SeedToYieldRatio
    #   Tie the SelectionCoefficient to also increase the SeedToYieldRatio over time.
    #   Add a WildSeedingRate and CultivationSeedingRate (number of kernels/ha) and remove CerealCultivationDensity

    # v0.5 to v0.6
    # Removed HunterGathererRatio (allows this to be an emergent property)
    # Added Gaussian filter to diet breadth logic
    # Added randomization of prey encounter number
    # Added Gaussian filter to coevolutionary selection and diffusion rates

    # v0.4 to v0.5
    # Updated variable names for readability

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
parser.add_argument('--HumanBirthRate', metavar='0.032', type=float, nargs='?', const=.032, default=.032, help='Enter the annual human per capita birth rate')
parser.add_argument('--CerealSelectionRate', metavar='0.03', type=float, nargs='?', const=.03, default=.03, help='Enter the coefficient of selection (e.g., the rate of change from wild-type to domestic type)')
parser.add_argument('--CerealCultivationDensity', metavar='1000000', type=int, nargs='?', const=1000000, default=1000000, help='Enter the number of additional millet plants to added to a patch each year due to proto cultivation of the patch. The patch reduces by the same number if not exploited.')
parser.add_argument('--label', metavar='Z.ZZ', nargs='?', const='1.01', default='1.01', help='This is the experiment and run number. E.g., experiment 1, run 1, should look like: 1.01')
###############################################################
## EDIT THESE VARIABLES AS YOU SEE FIT
# HUMAN VARIABLES
People = 50         ## Enter the initial number of people in the band
MaximumPeople = 3000    ## Enter the maximum human population (just to keep this in the realm of possibility, and to help set the y axis on the plot)
HumanBirthRate = 0.032         ## Enter the annual human per capita birth rate
HumanDeathRate = 0.03        ## Enter the annual human per capita death rate
HumanBirthDeathFilter = 0.005 ## Width of the Gaussian randomizing filter for human birth and death rates
StarvationThreshold = 0.8    ## Enter the starvation threshold (percentage of the total kcal below which people are starving, and effective reproduction goes to 0)
HumanKcal = 912500.0    ## Enter the number of kcals per year required per person
                            # 547500 for a 1500 kcal diet,730000.0 for a 2000kcal diet, 912500 for a 2500kcal diet, or 1095000.0 for a 3000kcal diet
ForagingHours = 4380       ## Enter the number of foraging hours available per person
                                # 4380 for 12hrs/day
ForagingUncertainty = 0.1        ## Width of the Gaussian randomizing filter that is applied to foraging payoff numbers in the forager's Diet Breadth decision algorithm
# PREY VARIABLES
Prey = 200         ## Enter the initial number of Prey in the hunting region
MaxPrey = 500     ## Enter the maximum number of Prey that the region can sustain (carrying capacity) without human predation
MaxPreyMigrants = 0        ## Enter the maximum number of new Prey that migrate into the territory each year (keeps Prey pop from being totally wiped out)
PreyBirthRate = 0.06        ## Enter the annual per capita birth rate for Prey
PreyDeathRate = 0.04        ## Enter the annual per capita natural death rate for Prey
PreyBirthDeathFilter = 0.005 ## Width of the Gaussian randomizing filter for prey birth and death rates
PreyReturns = 200000.0        ## Enter the return rate (number of kcals) per Prey killed
PreySearchCost = 72.0        ## Enter the density dependent search costs for Prey (hours time expended per recovery of one Prey at the density "PreyDensity")
PreyDensity = 1000        ## Density of Prey for which search cost prey search costs are known
MaxPreyEncountered = 4.0        ## Maximum number of individual Prey encountered per discovery
MinPreyEncountered = 1.0        ## Minimum number of individual Prey encountered per discovery
PreyHandlingCost = 16.0        ## Enter the handling costs for Prey (hours handling time expended once encountered)
# CEREAL VARIABLES
Cereal = 100        ## Enter the number of Cereal patches in the gathering region (assume a patch is ~1ha)
WildCerealReturns = 0.05        ## Enter the return rate (number of kcals) per wild-type Cereal seed
DomesticatedCerealReturns = 0.1        ## Enter the return rate (number of kcals) per domestic-type Cereal seed
WildToDomesticatedProportion = 0.98        ## Enter the starting proportion of wild-type to domestic-type Cereal (1.0 = all wild, 0.0 = all domestic)
CerealSelectionRate = 0.03        ## Enter the coefficient of selection (e.g., the rate of change from wild-type to domestic type)
CerealDiffusionRate = 0.02        ## Enter the coefficient of diffusion for Cereal (the rate at which selected domestic traits disappear due to crossbreeding)
SelectionDiffusionFilter = 0.001   ## Enter the width of the Gaussian filter applied to selection and diffusion rates.
CerealSearchCosts = 1.0        ## Enter the search costs for Cereal (hours expended to find one patch of Cereal)
CerealDensity = 10000000    ## Number of Cereal kernels that are harvested per patch at the start of the simulation
MaxCerealDensity = 100000000 ## Maximum number of Cereal kernels that can be harvest per patch (a bit of a teleology, but we need a stopping point)
CerealCultivationDensity = 1000000 ## Number of additional Cereal kernels that can be harvested from a patch each year due to proto-cultivation of the patch (up to maximum density). The patch yield reduces by the same number if not exploited (down to minimum)
WildCerealHandlingCost = 0.0001        ## Enter the handling costs for wild Cereal (hours handling time expended per seed once encountered)
DomesticatedCerealHandlingCost = 0.00001        ## Enter the handling costs for domestic Cereal (hours handling time expended per seed once encountered)
# SIMULATION CONTROLS
Years = 3000        ## Enter the number of years for which to run the simulation

# DO NOT EDIT BELOW THIS LINE
#############################################################
#############################################################
#############################################################

#Get values from command line variables
args = vars(parser.parse_args())
HumanBirthRate = args["HumanBirthRate"]
CerealSelectionRate = args["CerealSelectionRate"]
CerealCultivationDensity = args["CerealCultivationDensity"]
label = args["label"]
#Make some custom functions for the population dynamics

def babymaker(p, f, n):
    '''p is the per capita birth rate, f is the width of the Gaussian filter, n is the population size'''
    babys = np.round(np.random.normal(p,f)*n)
    return(babys)

def deathdealer(p, f, n):
    '''p is the per capita death rate, f is the width of the Gaussian filter, n is the population size'''
    deaths = np.round(np.random.normal(p,f)*n)
    return(deaths)


if __name__ == "__main__":
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
    ####### The simulation starts here.
    for year in range(1,Years+1):        #this is the outer loop, that does things at an annual resolution, counting the years down for the simulation
        kcalneed = People * HumanKcal        # find the number of kcals needed by the band this year
        timebudget = People * ForagingHours       # find the time budget for the band this year
        Prey_now = Prey            #set up a variable to track Prey population exploitation this year
        Cereal_now = Cereal        #set up a variable to track Cereal patch exploitation this year
        eatCereal = 0        #set up data container to count how many Cereal patches we ate this year
        eatPrey = 0        #set up data container to count how many Prey we ate this year
        while kcalneed > 0:        #this is the inner loop, doing foraging within the year, until kcal need is satisfied
            if Prey_now <= 0 and Cereal_now <= 0:
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
                    Preyscore = 0
                    pass
                if Prey_now <= 0: #if they killed all the Prey, then go to Cereal if possible
                    Preyscore = 0.
                    pass
                else:
                    kcalneed = kcalneed - PreyReturns ## QUESTION: should this be the return for a Prey minus the search/handle costs?? Or is that included in the daily dietary need (i.e., the energy expended searching and processing foodstuffs)
                    timebudget = timebudget - (PreySearchCost_Now + (PreyHandlingCost * PreyEncountered_Now))
                    eatPrey = eatPrey + PreyEncountered_Now
                    Prey_now = Prey_now - PreyEncountered_Now
            elif np.random.normal(Preyscore, Preyscore * ForagingUncertainty) > np.random.normal(Cerealscore, Cerealscore * ForagingUncertainty): # Harvesting cereal is more profitable
                if timebudget <= 0:
                    Cerealscore = 0
                    pass
                if Cereal_now <= 0: #if Cereal is all gone, then go back to Prey
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
                        Preyscore = 0
                        pass
                    if Prey_now <= 0: #if they killed all the Prey, then go to Cereal if possible
                        Preyscore = 0.
                        pass
                    else:
                        kcalneed = kcalneed - PreyReturns ## QUESTION: should this be the return for a Prey minus the search/handle costs?? Or is that included in the daily dietary need (i.e., the energy expended searching and processing foodstuffs)
                        timebudget = timebudget - (PreySearchCost_Now + PreyHandlingCost)
                        eatPrey = eatPrey + PreyEncountered_Now
                        Prey_now = Prey_now - PreyEncountered_Now
                else:
                    if timebudget <= 0:
                        Cerealscore = 0
                        pass
                    if Cereal_now <= 0: #if Cereal is all gone, then go back to Prey
                        Cerealscore = 0
                        pass
                    else:
                        kcalneed = kcalneed - (CerealReturns * CerealDensity_now)
                        timebudget = timebudget - CerealSearchCosts - (CombinedCerealHandlingCost * CerealDensity_now)
                        eatCereal = eatCereal + 1
                        Cereal_now = Cereal_now - 1
            if timebudget <= 0:        #check if they've run out of foraging time, and stop the loop if necessary.
                break
            if Prey <= 0 and Cereal <= 0:    #check if they've run out of food, and stop the loop if necessary.
                break
            if Preyscore <= 0 and Cerealscore <= 0:    #check if they've run out of food, and stop the loop if necessary.
                break
        ####### Now that the band has foraged for a year, update human, Prey, and Cereal populations, and implement selection
        if (People * HumanKcal) - kcalneed <= (People * HumanKcal * StarvationThreshold):     #Check if they starved this year and just die deaths if so
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
    ######
    ###### Simulation has ended, write stats
    GeneralStatsFile = '%s%sSimulation_general_stats.%s.csv' % (os.getcwd(), os.sep, label)
    statsout = pd.DataFrame(data=np.array([yr, HumPop, HumanKcalPrey, PreyPop, PreyKilled, CerealPop, CerealExploited, ProportionDomesticated, AverageCerealDensity]).T, columns = ["Year","Total Human Population","Human Kcal Deficit","Total Prey Animals Population","Number of Prey Animals Eaten","Total Cereal Population (*10^3)","Number of Cereal Patches Exploited","Proportion of Domestic-Type Cereal","Average Cereal Patch Density (*10^3)"])      # put the main stats data in a pandas data frame for easy formatting
    statsout.to_csv(GeneralStatsFile, float_format='%.5f')
    CerealDensityStatsFile = '%s%sSimulation_millet_patch_density_stats.%s.csv' % (os.getcwd(), os.sep, label)
    patchdens_ts.to_csv(CerealDensityStatsFile, float_format='%.5f')
    CerealProportionStatsFile = '%s%sSimulation_millet_patch_domestic_proportion_stats.%s.csv' % (os.getcwd(), os.sep, label)
    patchprop_ts.to_csv(CerealProportionStatsFile, float_format='%.5f')
    sys.exit(0)

