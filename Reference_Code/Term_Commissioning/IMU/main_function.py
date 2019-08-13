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
    
imu = bno055.bno055(pyb.I2C(1, I2C.MASTER, baudrate = 100000), 0x28)

while True:
#    pitch = i2c.mem_read(2, 0x28, 0x1A)
#    print(ustruct.unpack('<h',pitch))
#    print(str(pitch) + '\n')
    pitch = imu.get_euler_pitch()
    roll = imu.get_euler_roll()
    yaw = imu.get_euler_yaw()
    print(str(pitch) + ',' + str(roll) + ',' + str(yaw) + '\n')
    utime.sleep_ms(10)
    