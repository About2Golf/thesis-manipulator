"""
Created on Thu Jan 11 21:19:40 2018

@author: mecha10, JGrillo, TGoehring, TPeterson
"""
import pyb
import machine

class MotorDriver:
    ''' This class implements a motor driver for the
    ME405 board.
    either  MotorDriver(3, pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5)
            MotorDriver(5, pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1)
    '''

    def __init__ (self, EN_Pin, step_pin, dir_pin, Diag0_pin, Diag1_pin):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. '''

        ## Set Pin PA10 toas open-drain output with pull up resistors
        self.enable = pyb.Pin(EN_Pin,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
        self.step = pyb.Pin(step_pin,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
        self.dir = pyb.Pin(dir_pin,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
        self.diag0 = machine.Pin(Diag0_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.diag1 = machine.Pin(Diag1_pin, machine.Pin.IN, machine.Pin.PULL_UP)

        self.enable.low()                                         # Set Pins Low on startup
        self.step.low()
        self.dir.low()
        print ('Motor successfully initialized')

        # ## Set Pin PB4 as push-pull with the correct alternate function (timer)
        # self.Pin_1=pyb.Pin(Pin_1, pyb.Pin.AF_PP,af=2)
        # ## Set Pin PB5 as push-pull with the correct alternate function (timer)
        # self.Pin_2=pyb.Pin(Pin_2, pyb.Pin.AF_PP,af=2)
        # self.timer= pyb.Timer(timer, freq=20000)                             # Set Timer 3 to a frequency of 20,000 Hz
        # self.ch1 = self.timer.channel(1, pyb.Timer.PWM, pin=self.Pin_1) # Set Timer 3 Channel 1 to PWM for pin PB4
        # self.ch2 = self.timer.channel(2, pyb.Timer.PWM, pin=self.Pin_2) # Set Timer 3 Channel 2 to PWM for pin PB5

    def set_direction (self, direction):
        ''' This method sets the direction of the motor.
        @param direction Either 1 or -1'''
        if (direction > 0):
            self.dir.high()
        else:
            self.dir.low()

    def generate_pulse (self, level):
        ''' This method turns on the step pin for pulse generation.
        @param level Either 1 or 0'''
        #print ('Setting duty cycle to ' + str (level))
        if (level):
            self.step.high()
        else:
            self.step.low()
        # if (level >= 0):
        #     self.ch1.pulse_width_percent(0)
        #     self.ch2.pulse_width_percent(level)
        # else:
        #     self.ch2.pulse_width_percent(0)
        #     self.ch1.pulse_width_percent(-level)
        # self.EN_Pin.high()

    def enable_motor (self):
        ''' This method turns on the motor.'''
        self.enable.high()

    def disable_motor (self):
        ''' This method turns off the motor.'''
        self.enable.low()

    def read_diagnostics (self):
        ''' This method returns the values of the diagnostics pins.
        @return diag0 The status of the motor Diag0 Pin
        @return diag1 The status of the motor Diag1 Pin'''
        return (self.diag0.value(), self.diag1.value())
