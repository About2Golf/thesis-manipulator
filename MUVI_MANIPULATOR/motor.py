"""
Created on Thu Jan 11 21:19:40 2018

@author: mecha10, JGrillo
"""
import pyb
import micropython
import machine

class TMC2160Driver:
    '''
    '''

    def __init__ (self, step_pin, dir_pin, enable_pin, dco_pin, step_timer, step_channel, accel_timer, accel_ch, name):
        '''
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
        '''
        if steps == 0:
            return
        self.DONE = 0
        # print('move_to')
        # print(steps)
        self.total_steps = 2*steps
        accel1 = round(self.total_steps*0.20)
        accel2 = round(self.max_step_rate*self.init_speed/self.accel_rate)
        self.accel_steps = min(accel1,accel2)
        self.steps_to_stop = self.total_steps - self.accel_steps
        self.stepping = 1
        self.accelerating = 1

    def stop(self):
        '''
        Method to turn off the step generator.
        '''
        self.stepping = 0
        self.accelerating = 0
        self.step_count = 0
        self.total_steps = 0
        self.step_rate = self.init_speed
        self.DONE = 1

    def cb(self, tim):
        '''
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
                self.stepping = 0
                self.accelerating = 0
                self.step_count = 0
                self.total_steps = 0
                self.step_rate = self.init_speed
                self.step_timer.freq(self.step_rate)
                self.DONE = 1
        else:
            self.step.value(0)

    def accel_cb(self, tim):
        '''
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
        ''' This method sets the direction of the motor.
        @param direction Either 1 or 0'''
        if (direction > 0):
            self.dir.value(1)
        else:
            self.dir.value(0)
        # print('dir')
        # print(direction)

    def set_init_speed(self,init_speed):
        '''
        '''
        self.init_speed = init_speed
        self.set_step_freq(self.init_speed)
        # print('init_s')
        # print(init_speed)

    def set_max_speed(self,max_step_rate):
        '''
        '''
        self.max_step_rate = max_step_rate
        # print('max_s')
        # print(max_step_rate)

    def set_accel_rate(self,accel_rate):
        '''
        '''
        self.accel_rate = accel_rate
        self.accel_timer.freq(self.accel_rate)
        # print('accel')
        # print(accel_rate)

    def set_step_freq(self,step_rate):
        '''
        '''
        self.step_rate = step_rate
        self.step_timer.freq(self.step_rate)

    def enable_motor (self):
        ''' This method turns on the motor.'''
        self.enable.value(0)

    def disable_motor (self):
        ''' This method turns off the motor.'''
        self.enable.value(1)

    def is_done (self):
        '''
        '''
        return self.DONE
