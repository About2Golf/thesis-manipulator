"""
Created on Thu Jan 11 21:19:40 2018

@author: mecha10, JGrillo, TGoehring, TPeterson
"""
import pyb

class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board. '''
    
    def __init__ (self):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. '''
        print ('Creating a motor driver') 
        ## Set Pin PA10 toas open-drain output with pull up resistors
        self.pinPA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_OD, pull = pyb.Pin.PULL_UP)
        ## Set Pin PB4 as push-pull with the correct alternate function (timer)
        self.pinPB4 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.AF_PP, af=2) 
        ## Set Pin PB5 as push-pull with the correct alternate function (timer)
        self.pinPB5 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.AF_PP, af=2) 
        self.tim3 = pyb.Timer(3, freq = 20000)                          # Set Timer 3 to a frequency of 20,000 Hz
        self.ch1 = self.tim3.channel(1, pyb.Timer.PWM, pin=self.pinPB4) # Set Timer 3 Channel 1 to PWM for pin PB4
        self.ch2 = self.tim3.channel(2, pyb.Timer.PWM, pin=self.pinPB5) # Set Timer 3 Channel 2 to PWM for pin PB5
        self.pinPA10.low()  # Set Pins Low on startup 
        self.pinPB4.low()
        self.pinPB5.low()

    def set_duty_cycle (self, level):
        ''' This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
            cycle of the voltage sent to the motor '''
#        print ('Setting duty cycle to ' + str (level))     
        if (level >= 0):                        # Check if level is positive
            self.ch1.pulse_width_percent(0)     # Send CW signal (or vice versa)
            self.ch2.pulse_width_percent(level)
        else:                                   # Otherwise send CCW signal
            self.ch2.pulse_width_percent(0)     # (or vice versa)
            self.ch1.pulse_width_percent(-level)
        self.pinPA10.high()