
#HW 0: It's a plot
#Author: Thomas Goehring
#Created: 180120a
#Edited: 180121a
#Write a Python program for a PC which plots data from a csv (comma seperated) file on a graph
#The file will be named eric.csv

from matplotlib import pyplot			#import pyplot from matplot library

xdata = []								#intialize xdata, ydata, lines
ydata = []
lines = []

with open('RC_StepResponse.csv') as a_file:		#send eric.csv to a_file
	lines = a_file.readlines()			#create list of lines
for line in lines:						#for loop that sorts data in lines	
	num_strs = line.split(',')			#split data where in line where commas are present
	try:								#try if x and y are float values
		x = float(num_strs[0])			
		y = float(num_strs[1])
	except (IndexError, ValueError):	#if an Index Error or Value Error is present, pass on line	
		pass
	else:								#Otherwise append x and y to the x,y data arrays respectively
		#print(x ,y)
		xdata.append(x)
		ydata.append(y)
		
#pyplot.plot(xdata, ydata)				#plot data
#pyplot.title('Damped Exponential Decay')
#pyplot.xlabel('X Data')
#pyplot.ylabel('Y Data')
#pyplot.show()							#show plot


#with pyplot.xkcd():						#Create and XKCD style plot
fig = pyplot.figure()
pyplot.plot(xdata,ydata)
pyplot.title('RC_StepResponse')
pyplot.xlabel('Time (ms)')
pyplot.ylabel('Voltage (V)')
pyplot.tight_layout()
pyplot.show()


