"""
Created on Thu Jan 11 21:19:40 2018

@author: mecha10, JGrillo, TGoehring, TPeterson
"""
import pyb
import machine

# Motor rotation direction
CLOCKWISE = 1
COUNTERCLOCKWISE = -1

# Motor driver state
ENABLED = 1
DISABLED = -1

class StepperDriver:
    '''
    '''

    def __init__ (self, EN_Pin, step_pin, dir_pin, Diag0_pin, Diag1_pin, timer, channel):
    # def __init__(self, motor_steps, dir_pin, step_pin,
    #              enable_pin=None, pin_mode=GPIO.BOARD, microsteps=1, rpm=60):
        '''
        '''
        self.enable = pyb.Pin(EN_Pin,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
        self.step = pyb.Pin(step_pin,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
        self.dir = pyb.Pin(dir_pin,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
        self.diag0 = machine.Pin(Diag0_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.diag1 = machine.Pin(Diag1_pin, machine.Pin.IN, machine.Pin.PULL_UP)

        self.timer= pyb.Timer(timer, freq=20000)                             # Set Timer 3 to a frequency of 20,000 Hz
        self.ch1 = self.timer.channel(1, pyb.Timer.PWM, pin=self.Pin_1) # Set Timer 3 Channel 1 to PWM for pin PB4
        self.ch2 = self.timer.channel(2, pyb.Timer.PWM, pin=self.Pin_2) # Set Timer 3 Channel 2 to PWM for pin PB5
        self.ch1.pulse_width_percent(50)

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

    def accelerate(self):
        '''
        Method to turn on the increase the step rate.
        '''

    def constant_speed(self):
        '''
        Method to maintain current step rate.
        '''

    def decelerate(self):
        '''
        Method to turn decrease the step rate.
        '''

    def turn_off(self):
        '''
        Method to turn off the step generator.
        '''
    def set_setpoint(self, new_setpoint):
        '''
        Method to enable the user to define a new setpoint that the
        control loop will use as a reference value.
        @param new_setpoint: User-defined setpoint that the controller uses as its reference value
        '''
        self.setpoint = new_setpoint

    def set_ramp_parameters(self, new_period, new_speed, new_accel):
        ''' Method to change the stepper motor frequency.
        '''
        self.max_speed = new_speed
        self.accel_rate = new_accel
        self.timer.period(new_period)

        # #define CLOCK_CYCLES_PER_SECOND  72000000
        # #define MAX_RELOAD               0xFFFF
        #
        # uint32_t period_cycles = CLOCK_CYCLES_PER_SECOND / freq;
        # uint16_t prescaler = (uint16)(period_cycles / MAX_RELOAD + 1);
        # uint16_t overflow = (uint16)((period_cycles + (prescaler / 2)) / prescaler);
        # uint16_t duty = (uint16)(overflow / 2);


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
