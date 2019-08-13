"""
Created on Fri Jan 26 16:51:33 2018

@author: mecha10
"""

import serial
from matplotlib import pyplot

def plot_data(data_list,plot_title ='X versus Y', xtitle = 'X', ytitle = 'Y'):
    ''' 
    The purpose is to plot data from a step response of Position (ticks vs. 
    time (ms). The script splits data by commas and test for valid values. 
    The script handles appropriate errors (Value and Index) for added 
    robustness. 
    
    @param fileName: list containing data to sort
    @param plot_title: descriptive title of the plot/data
    @param xtitle: abscissa axis label
    @param ytitle: ordinate axis label
    
    @return: plot of X vs Y with plot title and axis labels
    '''
    
    x_data = []         # abscissa
    y_data = []         # ordinate
    value_errors = 0    # variable to count number of errors found in csv file
    index_errors = 0
    
    for line in data_list:
        list_line = line.split(',')     # separate data by "," delimiter
        try:
            x = float(list_line[0])     # attempt to float the data in column
            y = float(list_line[1])
        except (ValueError,IndexError):
            if ValueError:              # counter for vaulue errors
                value_errors += 1
            elif IndexError:            # counter for index errors
                index_errors += 1
        else:
            x_data.append(x)            # if successful, append data to x array
            y_data.append(y)            # same for y ^^

#with pyplot.xkcd():    
    print(x_data)
    print(y_data)
    #pyplot.clf()                        #Clear old plot data
    pyplot.plot(x_data,y_data)
    pyplot.autoscale(enable=True,axis='both',tight=None) # http://nullege.com/codes/search/matplotlib.pyplot.autoscale
    pyplot.title(plot_title)
    pyplot.xlabel(xtitle)
    pyplot.ylabel(ytitle)
    pyplot.show()
    print('Errors Found in Data:')
    print('ValueErrors: ', value_errors)
    print('IndexErrors: ', index_errors)
     
# --------------------------------------------------------------------------- #
#                                         Runs The Code
# --------------------------------------------------------------------------- #
    
#ser_port = serial.Serial('COM5',115200, timeout = 0.1)
    
data_list = []

with serial.Serial('/dev/ttyACM0',115200, timeout = .1) as ser_port:
    #ser_port.open()  The port is already open  
    ser_port.write(b'\x03')    
    ser_port.write(b'\x04')    
    ser_port.write(b'\n')
    for count in range(50):    
        data = (ser_port.readline()).decode('UTF-8')
        data_list.append(data)
    plot_data(data_list,plot_title = 'Step Response, 15 Degrees, Kp=1, Ki=.0125',xtitle = 'Time [ms]', ytitle = 'Position [ticks]')    