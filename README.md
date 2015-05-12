# AgModel
 
## An _Agent-Based Model_ of the forager-farmer transition ##

[![DOI](https://zenodo.org/badge/12885/isaacullah/AgModel.svg)](http://dx.doi.org/10.5281/zenodo.17551)

 This is an agent-based model of a potential scenario for the forager-farmer transition. It is parameterized  for a millet/deer ecosystem (east Asia), but could apply to any hunting/seed gathering system if parameterized accordingly. Rather than use an existing ABM or other modeling framework, I have written it in pure Python, both as a fun exercise for me, and with the hope of better integration to scientific Python (e.g., pandas, matplotlib) and the open-science movement.

 The model consists of a single software agent that, conceptually, can be thought of as a single hunter-gather community (i.e., a co-residential group that shares in subsistence activities and decision making). The model assumes a logistic, central-place foraging strategy in a fixed territory for a two-resource economy (see below for alternative mobility strategies). The territory has a fixed number of millet patches, and a starting number of deer. Note that while the model is not spatially explicit, it does assume some spatiality of resources (covered by search times).

 The simulation takes place at an annual temporal resolution, although there are many foraging decisions that will be made within each year (i.e., it is also "event" based). Each new year, the foraging agent must make a series of optimal foraging decisions based on its knowledge of the availability the two resources in the model: millet and deer (other resources are ignored, and the kcal intake from other resources should not be counted towards the total number of kcals that the foraging agent uses to calculate its decisions). The agent proceeds to balance the net benefits of the chance of finding, processing, and consuming a deer, versus that of finding a millet patch, and processing and consuming that millet. These decisions continue until the annual kcal target is reached (balanced on the current human population). If the agent consumes all available resources in a given year, it may "starve". Starvation will affect birth and death rates, as will foraging success. The initial birth and death rates of humans will thus change over time, and population will increase or decrease according to a probabilistic function (perturbed by some stochasticity) and the agent's foraging success or failure. 

 Deer populations recover/grow according to a similar birth/death rate ratio, with the addition of extra deaths caused by human predation. A small amount of deer may "migrate" into the territory each year. This prevents deer populations from complete decimation, but also may be used to model increased distances of logistic mobility (or, perhaps, even residential mobility within a larger territory). Search times for deer are entered for a known quantity of deer (default = 1000) so that the actual search time is the entered search time multiplied by the ratio of the current population to this "benchmark" population. Note also, that it is possible to increase the number of individual deer per encounter (which would reduce the search time per animal, accordingly).

 If agents consume millet, then their selection preferences will drive evolutionary processes within the millet population (selection rate is set at the start of the simulation). Two parameters are selected for: morphology (grain size/easy of harvesting), and patch density (reseeding density). These rates will increase over time in patches that are under consistent use (due to selection), but will begin to decrease in patches that are not used (according to a diffusion rate, and the proportion of wild to domesticated millet in all patches). Morphologically wild millet produces fewer kcal per seed, and has longer handling times. Thus, as millet is more frequently used, it's desirable traits are enhanced (via selection), and it becomes more profitable. Vice versa as millet is used less frequently. Currently, millet patches are accessed in the same order every year, so humans are assumed to be "choosing" the "best" patches first (planned model enhancement will allow this to change). The "size" of individual millet patches is set by the wild/domesticated millet patch density (default values assume patch size = 1 ha).

### References ###

The model is derived/inspired by ideas and data from the following scholarly works:

1. Bettinger, R.L., Barton, L., Morgan, C.T., 2010. The origins of food production in North China: a different kind of agricultural revolution, Evolutionary Anthropology 19, 9-21.

2. Winterhalder, B., Baillargeon, W., Cappelletto, F., Daniel, J., Prescott, I.R., 1988. The population ecology of hunter-gatherers and their prey, Journal of Anthropological Archaeology 7, 289-328.

3. Belovsky, G.E., 1988. An optimal foraging-based model of hunter-gatherer population dynamics, Journal of Anthropological Archaeology 7, 329-372.


## Installation and Running ##
 You will need to install [Python 2.7](www.python.org/download/releases/2.7/) to run it. You will need some additional python modules too, which can be installed various ways, depending on your system and preference. The modules you'll need are: [NumPy](www.numpy.org), [Pandas](pandas.pydata.org), [Matplotlib](matplotlib.org), and [EasyGUI](easygui.sourceforge.net). These are all available from the [PIP Python installer](github.com/pypa/pip), which is my preferred method of installation.

 Once these are all installed, you just place the script in a folder of your choosing, open a terminal window in that same directory (you can often do this from the "right click" pop-up menu), and type `python AgModel-0.3.py`. The first window that will pop up will ask for a configuration file. I include a sample config file in this github repo that will parametrize the model for some interesting dynamics, but you need not load one. There are default values that will populate the fields. If you want to just load up the default values, hit cancel on this window. It will then ask you to save a new config file, and you should do that if you're going to be changing any values and want to save them for another time. Then, there will be several windows showing you the variables, and allowing you to change them. Anything you change will be saved to that config file you just made (and so you can load them up again that way later). Once you've adjusted the parameters, the plotting canvas window will pop up, and it will ask you to if you want to start the simulation. Hit "OK", and the model begins to run. There is some informative text that gets written to the terminal during the simulation, and the plots will be updated on the fly, so you will be able to see what's going on in the simulation. Once it's finished, you get the option of saving some output stats files, as well as the plots themselves. You can save any or all of these, but make sure to select the ones you want to make on the first screen. Then, you can exit the simulation, and do it all over again!

### Notes ###

* This software is released under the [GPL license](http://www.gnu.org/copyleft/gpl.html).
* Current release number is v0.3, which is a fully functional beta.
* Please cite as: __"Isaac I. Ullah, 2015. AgModel, version 0.3. http://dx.doi.org/10.5281/zenodo.17551"__ if you publish anything related to this software.
* Citations to scholarly work that employs this software will be listed here in future.

## Model Variables ##

 Here is a table of the input variables in the model, their default values, and a brief description of the variable.

<center>**Human Variables**</center>

Variable	| Default Value | Description
----------- | ------------- | ---------------------------------------------------------------------------------------------------------------------
people 		| 50.0   		| The initial number of people in the band
maxpeople 	| 500 			| The maximum human population (just to keep this in the realm of possibility, and to help set the y axis on the plot)
hbirth 		| 0.04   		| The annual human per capita birth rate
hdeath 		| 0.03  		| The annual human per capita death rate
starvthresh | 0.8 			| The starvation threshold (percentage of the total kcal below which people are starving, and effective reproduction goes to 0)
hkcal 		| 547500.0 		| The number of kcals per year rquired per person
fhours 		| 4380  		| The number of foraging hours available per person

<center>**Deer variables**</center>

Variable	| Default Value | Description
----------- | ------------- | ---------------------------------------------------------------------------------------------------------------------
deer 		| 4000.0  		| The inital number of deer in the hunting region
maxdeer 	| 6000.0  		| The maximum number of deer that the region can sustain (carrying capacity) without human predation
dmigrants 	| 10  			| The number of new deer that migrate into the territory each year (keeps deer pop from being totally wiped out)
dbirth 		| 0.065  		| The annual per capit birth rate for deer
ddeath 		| 0.02  		| The annual per capita natural death rate for deer
dret 		| 158000.0   	| The return rate (number of kcals) per deer killed
ddsrch 		| 72.0  		| The density dependant search costs for deer (hours time expended per recovery of one deer at the density "ddens")
ddens 		| 1000  		| Density of deer for which search cost "dsrch" is known
dpatch 		| 1.0  			| Number of individual deer encountered per discovery
dhndl 		| 16.0  		| The handling costs for deer (hours handling time expended per deer once encountered)

<center>**Millet Variables**</center>

Variable	| Default Value | Description
----------- | ------------- | ---------------------------------------------------------------------------------------------------------------------
millet 		| 500  			| The number of millet patches in the gathering region (assume a patch is ~1ha)
mretw 		| 0.0507  		| The return rate (number of kcals) per wild-type millet seed
mretd 		| 0.1014  		| The return rate (number of kcals) per domestic-type millet seed
mprop 		| 0.98  		| The starting proportion of wild-type to domestic-type millet (1.0 = all wild, 0.0 = all domestic)
mselect 	| 0.03  		| The coefficient of slection (e.g., the rate of change from wild-type to domestic type)
mdiffus 	| 0.02  		| The coefficient of diffusion for millet (the rate at which selected domestic traits dissappear due to crossbreeding)
msrch 		| 1.0  			| The search costs for millet (hours expended to find one patch of millet)
mpatch 		| 880000.0 		| Number of millet plants per patch at the start of the simulation (individuals encountered per discovery)
maxpatch 	| 1760000.0 	| Maximum number of millet plants that can be grown per patch (a bit of a teleology, but we need a stopping point for now)
cultiv 		| 5000 			| Number of additional millet plants to added to a patch each year due to proto cultivation of the patch. The patch reduces by the same number if not exploited.
mhndl 		| 0.0001  		| The handling costs for millet (hours handling time expended per seed once encountered)

<center>**Simulation Controls**</center>

Variable	| Default Value | Description
----------- | ------------- | ---------------------------------------------------------------------------------------------------------------------
years 		| 500  			| The number of years for which to run the simulation
