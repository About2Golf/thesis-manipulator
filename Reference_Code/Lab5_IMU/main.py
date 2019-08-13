#
### First order step response test
#
#"""
#
#@author: mecha10, JGrillo, TGoehring, TPeterson
#"""

import pyb
from pyb import I2C
import micropython
import ustruct
import utime
import bno055

#i2c = pyb.I2C(1, I2C.MASTER, baudrate = 115200)



#==============================================================================
# i2c.mem_write(0x0C, 0x28, 0x3D)
# utime.sleep_ms(10)
# 
# status = i2c.mem_read(1,0x28,0x39)
# print(ustruct.unpack('b',status))
# 
# error = i2c.mem_read(1,0x28,0x3A)
# print(ustruct.unpack('b',error))
#==============================================================================
    
imu = bno055.bno055()



while True:
#    pitch = i2c.mem_read(2, 0x28, 0x1A)
#    print(ustruct.unpack('<h',pitch))
#    print(str(pitch) + '\n')
    pitch = imu.get_euler_pitch()
    roll = imu.get_euler_roll()
    yaw = imu.get_euler_yaw()
    print(str(pitch) + ',' + str(roll) + ',' + str(yaw) + '\n')
    utime.sleep_ms(10)



















#
#import pyb
#import task_share
#
##Set up queue using task share, unsigned integers, queue size of 1000 with 
##thread protection for interrupts
#q0 = task_share.Queue ('I', 1000, thread_protect = True, overwrite = False,
#                           name = "Queue_0") 
#
##Set up PC1 as an output to the circuit
#PinPC1=pyb.Pin(pyb.Pin.board.PC1,pyb.Pin.OUT_PP, pull=pyb.Pin.PULL_UP)
##Set up PC0 as an input to the ADC
#PinPC0=pyb.Pin(pyb.Pin.board.PC0,pyb.Pin.IN)
##Timer 1 with a 1KHz frequency
#Timer= pyb.Timer(1, freq=1000)                             
##Set up ADC reading from PinPC0
#adcpin = pyb.ADC (PinPC0)
##Create tick function that receives the timer object when called 
#def tick(Timer): 
#    if not q0.full(): #if the queue is not full, load ADC 
#        volts = adcpin.read () #read ADC 
#        q0.put(volts,in_ISR=True) #Put volts into queue
#    else:
#        Timer.callback(None) #If full, turn off the interrupt
#
#if __name__ == "__main__":
#    print('Running the stupid code')    
#    PinPC1.high()
#    Timer.callback(tick)
#    while True:    
#        if q0.full():
#            PinPC1.low()            
#            xdata = [i for i in range(1000)]
#            ydata = []        
#            for i in range(1000):
#                queue = q0.get(in_ISR=False)  
#                ydata.append(queue)
#            for (time,voltage) in zip(xdata,ydata): # Referenced https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
#                print(str(time) + ',' + str(voltage))        
#                
#            
#      
#
