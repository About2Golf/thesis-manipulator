"""
Created on Thu Jan 11 21:19:40 2018

@author: mecha10, JGrillo, TGoehring, TPeterson
"""
import pyb

class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board.
    either  MotorDriver(3, pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5)
            MotorDriver(5, pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1)
    '''

    def __init__ (self, pin, timer, channel, alt_fun, name):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. '''
        ## Set Pin PA10 toas open-drain output with pull up resistors
        # self.EN_Pin=pyb.Pin(EN_Pin,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
        ## Set Pin PB4 as push-pull with the correct alternate function (timer)
        self.pin=pyb.Pin(pin, pyb.Pin.AF_PP,af=alt_fun)
        ## Set Pin PB5 as push-pull with the correct alternate function (timer)
        # self.Pin_2=pyb.Pin(Pin_2, pyb.Pin.AF_PP,af=2)
        self.timer= pyb.Timer(timer, freq = 2)                             # Set Timer 3 to a frequency of 20,000 Hz
        self.channel = self.timer.channel(channel, pyb.Timer.PWM, pin=self.pin) # Set Timer 3 Channel 1 to PWM for pin PB4
        # self.ch2 = self.timer.channel(2, pyb.Timer.PWM, pin=self.Pin_2) # Set Timer 3 Channel 2 to PWM for pin PB5
        # self.EN_Pin.low()                                         # Set Pins Low on startup
        self.pin.low()
        print('successfully created '+name)
        # self.Pin_2.low()

    def set_duty_cycle (self, level):
        ''' This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
            cycle of the voltage sent to the motor '''
        #print ('Setting duty cycle to ' + str (level))
        self.channel.pulse_width_percent(level)
        # if (level >= 0):
        #     self.ch1.pulse_width_percent(0)
        #     self.ch2.pulse_width_percent(level)
        # else:
        #     self.ch2.pulse_width_percent(0)
        #     self.ch1.pulse_width_percent(-level)
        # self.EN_Pin.high()

    def set_frequency (self, frequency):
        self.timer.freq(frequency)
