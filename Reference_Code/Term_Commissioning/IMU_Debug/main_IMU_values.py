"""
Created on Thu Jan 25 19:31:26 2018

@author: Jason Grillo, Thomas Goehring, Trent Peterson
"""

#Yellow Encoder Cable: B7
#Gray Encoder Cable: B6
 
import pyb
import BNO055


#Encoder_1  = encoder.Encoder(4,pyb.Pin.board.PB6,pyb.Pin.board.PB7)
IMU = BNO055.bno055 (pyb.I2C (1, pyb.I2C.MASTER, baudrate = 100000), micropython.const(0x28))

# Setup/Initialization
def setup():
    ''' This initializes the encoder and motor to zero values. '''
    IMU.zero_Euler_vals()    
    
# -------------------------------------------------------------------------#

        
# --------------------------------------------------------------------------- #
#                                         Runs The Code
# --------------------------------------------------------------------------- #
setup()
while(1):
    print(IMU.get_euler_roll())

    
    