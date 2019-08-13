# -*- coding: utf-8 -*-
"""
Spyder Editor

@author TG, JG, TP
"""

import pyb
from pyb import I2C
import micropython
import ustruct

_WHO_AM_I = micropython.const(0x28)

_CHIP_ID = micropython.const(0xa0)

CONFIG_MODE = micropython.const(0x00)
ACCONLY_MODE = micropython.const(0x01)
MAGONLY_MODE = micropython.const(0x02)
GYRONLY_MODE = micropython.const(0x03)
ACCMAG_MODE = micropython.const(0x04)
ACCGYRO_MODE = micropython.const(0x05)
MAGGYRO_MODE = micropython.const(0x06)
AMG_MODE = micropython.const(0x07)
IMU_MODE = micropython.const(0x08)
COMPASS_MODE = micropython.const(0x09)
M4G_MODE = micropython.const(0x0a)
NDOF_FMC_OFF_MODE = micropython.const(0x0b)
NDOF_MODE = micropython.const(0x0c)

_POWER_NORMAL = micropython.const(0x00)
_POWER_LOW = micropython.const(0x01)
_POWER_SUSPEND = micropython.const(0x02)

_MODE_REGISTER = micropython.const(0x3d)
_PAGE_REGISTER = micropython.const(0x07)
_TRIGGER_REGISTER = micropython.const(0x3f)
_POWER_REGISTER = micropython.const(0x3e)
_ID_REGISTER = micropython.const(0x00)

class bno055:
    """ This class implements a simple driver for the BNO055 Adafruit
    IMU. This IMU talk to the CPU over I<sup>2</sup>C. 
    Only basic functionality is supported: 
    * The device can be switched from standby mode to active mode and back
    * Readings from all three axes can be taken in A/D bits or in g's
    * The range can be set to +/-2g, +/-4g, or +/-8g
    
#    An example of how to use this driver:
#    @code
#    mma = mma845x.MMA845x (pyb.I2C (1, pyb.I2C.MASTER, baudrate = 100000), 29)
#    mma.active ()
#    mma.get_accels ()
#    @endcode 
    The example code works for an MMA8452 on a SparkFun<sup>TM</sup> breakout
    board. """

    def __init__ (self):
        """ Initialize an MMA845x driver on the given I<sup>2</sup>C bus. The 
        I<sup>2</sup>C bus object must have already been initialized, as we're
        going to use it to get the accelerometer's WHO_AM_I code right away. 
        @param i2c An I<sup>2</sup>C bus already set up in MicroPython
        @param address The address of the accelerometer on the I<sup>2</sup>C
            bus 
        @param accel_range The range of accelerations to measure; it must be
            either @c RANGE_2g, @c RANGE_4g, or @c RANGE_8g (default: 2g)
        """
        self.address = 0x28 #Address of the IMU (Hard Value)
        self._i2c = pyb.I2C(1, I2C.MASTER, baudrate = 100000) #Select I2C, Master and Baud rate
        self._i2c.mem_write(NDOF_MODE, self.address, _MODE_REGISTER) #Seelect NDOF mode, @IMU Hard address, Set NDOF_Mode to MODE_REGISTER
    
    def get_euler_pitch(self):
        self._pitch = self._i2c.mem_read(2, self.address, 0x1E) #Read 2 Pitch start at pitch lsb
        self._pitch_decode = ustruct.unpack('<h',self._pitch) #Unpact struct to get pitch value
        self._pitch_value = self._pitch_decode[0]/16
        return self._pitch_value
        
    def get_euler_roll(self):
        self._roll = self._i2c.mem_read(2, self.address, 0x1C)
        self._roll_decode = ustruct.unpack('<h',self._roll)
        self._roll_value = self._roll_decode[0]/16
        return self._roll_value

        
    def get_euler_yaw(self):
        self._yaw = self._i2c.mem_read(2, self.address, 0x1A)
        self._yaw_decode = ustruct.unpack('<h',self._yaw)
        self._yaw_value = self._yaw_decode[0]/16
        return self._yaw_value
        
    def sys_status(self):
         self._status = self._i2c.mem_read(1,self.address,0x39)
         self._status_decode = ustruct.unpack('b',self._status)
         return self._status_decode
         
    def sys_error(self):
         self._error = self._i2c.mem_read(1,self.address,0x3A)
         self._error_decode = ustruct.unpack('b',self._error)
         return self._error_decode
               
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        