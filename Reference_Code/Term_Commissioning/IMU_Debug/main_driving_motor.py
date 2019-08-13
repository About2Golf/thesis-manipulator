"""
Created on Thu Jan 25 19:31:26 2018

@author: Jason Grillo, Thomas Goehring, Trent Peterson
"""

#Yellow Encoder Cable: B7
#Gray Encoder Cable: B6
 
import pyb
import motor

# Create all objects
DC_Motor_1 = motor.MotorDriver(5,pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1)

# Setup/Initialization
def setup():
    ''' This initializes the encoder and motor to zero values. ''' 
    DC_Motor_1.set_duty_cycle(0)

    
# Continuous loop
def loop():
    ''' This is the main loop that handles the DC Motor step response
        functionality. '''      
    DC_Motor_1.set_duty_cycle(200)
        
# --------------------------------------------------------------------------- #
#                                         Runs The Code
# --------------------------------------------------------------------------- #

setup()
while(1):
    print('Start of Loop')
    loop()
    
    