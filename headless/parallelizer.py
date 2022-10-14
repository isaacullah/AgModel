#!usr/bin/python
import sys, os, time
from subprocess import Popen, list2cmdline
from itertools import product

##############################
## EDIT THESE VALUES -- They are the parameters to sweep through. Change names and values to fit the CLI command in cmdlist

v1list = (0.030,0.031,0.032,0.033) # List of values of variable 1 to sweep through
v1name = "hbirths" # Name of variable 1, for output files

v2list = (0.01,0.02,0.03,0.04) # List of values of variable 2 to sweep through
v2name = "mselect" #Name of variable 2, for output files

v3list = (1000,2000,3000,4000) # List of values of variable 2 to sweep through
v3name = "cultiv" #Name of variable 3, for output files

repeats = 10 # Number of times to repeat each experiment

expout = '%s%sSimulation_variables_and_numbers_list.csv' % (os.getcwd(), os.sep) # This is an output text file that will make a table of the experiment numbers and values

cmdout = False # Change to True to write all iterations of cmdlist to expout

## EDIT ONLY WHERE NOTED BELOW THIS LINE (LINE 94 ONLY)
##############################


def cpu_count():
    '''Returns the number of CPUs in the system'''
    num = 1
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            pass
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            pass

    return num


def exec_commands(cmds):
    ''' Execute commands in "parallel" as multiple processes across as
        many CPU's as are available'''
    if not cmds: return # empty list

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0
    def fail():
        sys.exit(1)

    max_task = cpu_count()
    processes = []
    while True:
        while cmds and len(processes) < max_task:
            task = cmds.pop()
            print(list2cmdline(task))
            processes.append(Popen(task))

        for p in processes:
            if done(p):
                if success(p):
                    processes.remove(p)
                else:
                    fail()

        if not processes and not cmds:
            break
        else:
            time.sleep(0.05)

if __name__ == "__main__":
    #create a list of variable combos ("Cartesian product")
    varlist = list(product(v1list, v2list, v3list))
    # write out experiments list to a file and assemble the command strings
    f = open(expout, 'w+') # Open up a text file to write out a list of the experiments to
    f.write("Experiment number,%s,%s,%s,repetitions\n" % (v1name,v2name,v3name))
    commands = []
    for i in range(len(varlist)):
        f.write("%s,%s,%s,%s,%s\n" % (i + 1, varlist[i][0], varlist[i][1], varlist[i][2], repeats)) # writing the experiment list to that file
        for x in range(repeats):

            ###EDIT THIS LINE
            cmdlist = ['python', 'Agmodel-0.4_headless.py', '--hbirth', '%s' % varlist[i][0], '--mselect', '%s' % varlist[i][1], '--cultiv', '%s' % varlist[i][2], '--label', '%s.%s' % (i + 1, str(x).zfill(len(str(repeats)))) ] # This is the main CLI command that will be constructed for each experiment. It must be in list form, with each CLI argument as an individual list element. Edit to match your model's CLI interface. NOTE that varible "varlist[i][1]" will be replaced by a numerical value from your list of values for the first variable, etc. Ensure that these variables appear at the proper place in the CLI for your model.
            ##STOP EDITING

            commands.append(cmdlist) # creating a CLI command for each experiment and repetition. and appending the current CLI command to the list
    if cmdout is True:
        for command in commands:
            f.write(" ".join(command) + "\n") # Writing the CLI command to experiment list text file, if we are told to do so
    f.close() # close text file

    exec_commands(commands) # execute all of the experiments using every available core until they are all done
    sys.exit(0)