"""
Created on Fri Jan 26 16:51:33 2018

@author: mecha10
"""
#from IPython import get_ipython
#get_ipython().magic('reset -sf')
import serial
from matplotlib import pyplot
import time

x_data = []         # abscissa
y_data = []         # ordinate

def plot_data(data_list,plot_title ='X vs Y Plot', xtitle = 'X', ytitle = 'Y'):
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
    
    #x_data = []         # abscissa
    #y_data = []         # ordinate
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
    end = len(x_data) - 5
    motor1_x = [x_data[i] for i in range(100)]
    motor1_y = [y_data[i] for i in range(100)]
    motor2_x = [x_data[i] for i in range(100, end)]
    motor2_y = [y_data[i] for i in range(100, end)]
#with pyplot.xkcd():    
#    print(x_data)
#    print(y_data)
    #pyplot.clf()                        #Clear old plot data
#    pyplot.plot(x_data,y_data)
    pyplot.plot(motor1_x,motor1_y, 'b--')
    pyplot.plot(motor2_x,motor2_y, 'r')
    pyplot.autoscale(enable=True,axis='both',tight=None) # http://nullege.com/codes/search/matplotlib.pyplot.autoscale
    pyplot.title(plot_title)
    pyplot.xlabel(xtitle)
    pyplot.ylabel(ytitle)
    pyplot.ylim(0,22000)
    pyplot.show()
    print('Errors Found in Data:')
    print('ValueErrors: ', value_errors)
    print('IndexErrors: ', index_errors)
     
# --------------------------------------------------------------------------- #
#                                         Runs The Code
# --------------------------------------------------------------------------- #
        
data_list_motor1 = []
data_list = []

with serial.Serial('/dev/ttyACM0',115200,timeout = .1) as ser_port:
    #ser_port.open()  The port is already open      
    ser_port.write(b'\x03')    
    ser_port.write(b'\x04')
    ser_port.write(b'\n')
    time.sleep(4)
    data_list_motor1[:] = []
    for count in range(250):    
        data = (ser_port.readline()).decode('UTF-8')
        data_list.append(data)        
#    if any("Motor 1:" in line for line in data_list):
#        for value in range(100):
#            data_list_motor1.append()
    plot_data(data_list,plot_title = 'Motor Step Response',xtitle = 'Time [ms]', ytitle = 'Position [ticks]')    