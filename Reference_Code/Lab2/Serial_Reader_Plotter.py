"""
Created on Fri Jan 26 16:51:33 2018

@author: mecha10
"""

import serial
import csv

comPort = '/dev/ttyACM0'
baudRate = 115200
ser = serial.Serial(comPort, baudRate)
test_number = 1


def csvWrite(data):
    with open(fileName,'a') as fp:
        w = csv.writer(fp)
        w.writerow()

while True:
    data = (ser.readline()).decode('UTF-8')
    if 'Running' in data:
        test_number += 1        
        fileName = 'StepResponse_' + str(test_number) + '.csv'        
        csvWrite(data,fileName)
