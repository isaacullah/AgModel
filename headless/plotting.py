import pylab as plt
import numpy as np

X = [0]
Y = [0]
Y2 = [0]
fig = plt.figure(figsize=(10,5))
plt.ion()
# Two subplots, the axes array is 1-d
ax1 = fig.add_subplot(211) # creates first axis
plt.title('Simulation output')
ax1.set_ylabel('population')
ax1.axis([0, 1000, 0, 500]) #set extents of x and y axes
ax2 = ax1.twinx()
#ax2 = fig.add_subplot(212, sharex=ax1) # creates second axis
ax2.axis([0, 1000, 0, 500]) #set extents of x and y axes
ax2.set_ylabel('food', color='r') # math colors of line to axis and ticks
for tl in ax2.get_yticklabels():
    tl.set_color('r')
ax2.set_xlabel('years')
p1, = ax1.plot(X, Y, 'k-') #Note the comma!!! Very important to have the comma!!!
p2, = ax2.plot(X, Y2, 'r-') #Note the comma!!! Very important to have the comma!!!
plt.setp( ax1.get_xticklabels(), visible=False)
plt.show()
raw_input('Press Enter to start the simulation')
for a in range(1,1001):
    X.append(a)
    Y.append(np.sqrt(X[a] * 100 * np.random.random() ) )
    Y2.append(np.sqrt(X[a] *100) )
    p1.set_data(X, Y)
    p2.set_data(X, Y2)
    plt.draw()
saveplt = raw_input('Simulation complete. Save the plot to a file? (y/N)')
if saveplt is 'y':
    pltname = raw_input('Enter the file name of the plot: ')
    if pltname is '':
        pltname = raw_input('You must enter a file name for the plot: ')
    plt.savefig('%s.svg'% pltname, format = 'svg', frameon = True)
exit(0)