"""
Created on Thu Jan 11 21:19:40 2018

@author: JGrillo
"""
import pyb
import micropython
import machine

class TMC2160Driver:
    '''
    This is the class definition for the stepper driver ICs. The hardware pins
    are defined, as well as the step generator and ramp accelerator.
    '''

    def __init__ (self, step_pin, dir_pin, enable_pin, dco_pin, step_timer,
                        step_channel, accel_timer, accel_ch, name):
        '''
        The initialization method for the stepper driver.
        @param step_pin - The step pin for the driver
        @param dir_pin - The direction pin for the driver
        @param enable_pin - The enable pin for the driver (active low)
        @param dco_pin - The DC step pin
        @param step_timer - The step generating timer
        @param step_channel - The step generator channel specific to the stage
        @param accel_timer - The ramp acceleration timer
        @param accel_ch - The ramp acceleration channel specific to the stage
        @param name - The name of the stage ('X' or 'Z' or 'Y' or 'P')
        '''
        # Initialize Stepper Driver Pins
        self.step =  machine.Pin(step_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.dir = machine.Pin(dir_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.enable = machine.Pin(enable_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.dco = machine.Pin(dco_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        # Initialize Default Ramp Parameters
        self.init_speed = 50
        self.step_rate = self.init_speed
        self.max_step_rate = 10000
        self.accel_rate = 50
        # Initialize Step and Acceleration Timers
        self.step_timer = pyb.Timer(step_timer, freq=self.step_rate)
        self.step_channel = self.step_timer.channel(step_channel, pyb.Timer.OC_TIMING, callback=self.cb)
        self.accel_timer = pyb.Timer(accel_timer, freq=self.accel_rate)
        self.accel_channel = self.accel_timer.channel(accel_ch, pyb.Timer.OC_TIMING, callback=self.accel_cb)
        # Initialize Profile Variables
        self.stepping = 0
        self.accelerating = 0
        self.paused = 0
        self.step_count = 0
        self.total_steps = 0
        self.steps_moved = 0
        self.name = name
        self.DONE = 1
        # Initialize Startup State
        self.enable.value(0)
        self.step.value(0)
        self.dir.value(0)
        string = self.name + 'Stepper Successfully Initialized'
        print (string)

    def move_to(self, steps):
        '''
        The command to move the motor a given number of steps.
        @param steps - The number of steps to move the motor.
        '''
        if steps == 0:
            return
        self.DONE = 0
        self.steps_moved = 0
        self.total_steps = 2*steps
        accel1 = round(self.total_steps*0.20)
        accel2 = round(self.max_step_rate*self.init_speed/self.accel_rate)
        self.accel_steps = min(accel1,accel2)
        self.steps_to_stop = self.total_steps - self.accel_steps
        self.stepping = 1
        self.accelerating = 1

    def stop(self):
        '''
        Method to deactivate the step generator and stop the motor.
        '''
        self.steps_moved = self.step_count
        self.stepping = 0
        self.accelerating = 0
        self.step_count = 0
        self.total_steps = 0
        self.step_rate = self.init_speed
        self.step_timer.freq(self.step_rate)
        self.DONE = 1

    def get_steps_moved(self):
        '''
        Method to get the number of steps the motor moved.
        @return steps_moved
        '''
        return self.steps_moved/2

    def cb(self, tim):
        '''
        The step generator interrupt callback function.
        @param tim - The timer interrupt instance
        '''
        if self.stepping:
            if self.step_count <= self.total_steps:
                # Comment Below for DC Step Operation
                self.step_count +=1
                if not self.step.value():
                    self.step.value(1)
                else:
                    self.step.value(0)
                # # Uncomment below for DC Step Operation
                # if self.dco_pin.value():
                #     self.paused = 0
                #     self.step_count +=1
                #     if not self.step.value():
                #         self.step.value(1)
                #     else:
                #         self.step.value(0)
                # else:
                #     self.paused = 1
            else:
                self.stop()
        else:
            self.step.value(0)

    def accel_cb(self, tim):
        '''
        The ramp accelerator interrupt callback function.
        @param tim - The timer interrupt instance
        '''
        if self.accelerating and not self.paused:
            if self.step_count <= self.accel_steps:
                if self.step_rate < self.max_step_rate:
                    self.step_rate += 1
                    self.step_timer.freq(self.step_rate)
            elif self.step_count >= self.steps_to_stop:
                if self.step_rate > self.init_speed:
                    self.step_rate -= 1
                else:
                    self.step_rate = self.init_speed
                self.step_timer.freq(self.step_rate)
        else:
            return

    def set_direction (self, direction):
        '''
        This method sets the direction of the motor.
        @param direction - Either 1 or 0
        '''
        if (direction > 0):
            self.dir.value(1)
        else:
            self.dir.value(0)

    def set_init_speed(self,init_speed):
        '''
        This method defines the initial step generator frequency in Hz.
        @param init_speed - The initial ramp speed
        '''
        self.init_speed = init_speed
        self.set_step_freq(self.init_speed)

    def set_max_speed(self,max_step_rate):
        '''
        This method defines the maximum step generator frequency in Hz.
        @param max_step_rate - The maximum step frequency of the motion.
        '''
        self.max_step_rate = max_step_rate

    def set_accel_rate(self,accel_rate):
        '''
        This method defines the acceleration frequency of the ramp in Hz/sec.
        @param accel_rate - The acceleration frequency.
        '''
        self.accel_rate = accel_rate
        self.accel_timer.freq(self.accel_rate)

    def set_step_freq(self,step_rate):
        '''
        This method sets the step generator timer frequency in Hz.
        @param step_rate - The frequency to set the step timer.
        '''
        self.step_rate = step_rate
        self.step_timer.freq(self.step_rate)

    def enable_motor (self):
        '''
        This method turns on the motor.
        '''
        self.enable.value(0)

    def disable_motor (self):
        '''
        This method turns off the motor.
        '''
        self.enable.value(1)

    def is_done (self):
        '''
        This method indicates whether or not the motor has finished moving.
        @return DONE
        '''
        return self.DONE
