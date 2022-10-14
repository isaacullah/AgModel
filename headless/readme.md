# AgModel_headless 

## What is this?

This is the "headless" version of AgModel. It is designed to be run without a GUI (i.e., from the command line). This makes it easier to run as a subprocess in some other code, or as a batch process. In particular, this mode is useful for conducting many repeated runs of an experiment or set of experiment. 

## How do I use it?

There is a sparse CLI API for four variables: *hbirth, cultiv, hmillet,* and *label*. All other variables can be set in the header of the script itself (use a text editor to change these) You can run the program from the command line with the defaults with the simple command `python3 AgModel_headless.py --hbirth 0.032 --cultiv 0.01....` and so on for the four variables you can access on the command line.

It's useful to use the GUI version to first explore the effects of the various variables and to get to know the expected output of the model. Then, you can set up a set of repeated runs in a short script where you set the specific variables on the command line. To aid this, I also provide the `parallelizer.py` script. This allows you to set up a series of experiments. You can set up the variables you want to step through, and set the variable values to step through. It will then create a contingency table that combines every possible combination of variables that you have entered. You can also specify how many times you want to repeat each of these unique combinations. It will then distribute each model run as a single process over all the available processors, and will continue to run each repetition for each scenario until all the experiments are finished. Since it automatically queues the experiments to run on the next available processor, it will finish all your scenarios in the most optimal amount of time given the number of processors in your computer. You must set up the parallelizer.py script by editing it in a text file as it does not have a CLI API.

Note that each repetition for each scenario will create a separate output plaintext CSV stats file containing the time series results for human, deer, and millet populations (same values as seen on the plots in the standard GUI version of the model). Since there is no GUI in which to view the model output, I also provide `plotter.py` and `stats_amalgamator.py` scripts that you can edit to produce some basic plots of experiment output. Note that you need to open these scripts in a text editor and edit some values for them to work with your particular output.
