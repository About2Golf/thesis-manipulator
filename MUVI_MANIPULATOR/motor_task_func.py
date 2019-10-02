"""
Created on Fri Feb  9 23:53:47 2018

@author: JasonGrillo
"""
import motor

import pyb
import micropython
import machine

class Motor_Task:
    '''
    '''

    def __init__(self, params_queue, enable_share, status_share, limit_share, step_pin, dir_pin, enable_pin, dco_pin, step_timer, step_channel, accel_timer, accel_ch, name):
        ''' Construct a motor task function by initilizing any shared
            variables and initialize the motor object
            @param coordinate The motor's queue variable with the step info
            @param EN_pin The Motor's CSN and Enable pin (shared)
            @param step_pin The motor's step pin
            @param dir_pin The motor's direction pin
        '''
        self.params = params_queue
        self.enable = enable_share
        self.status = status_share
        self.limit = limit_share
        self.Motor = motor.TMC2160Driver(step_pin, dir_pin, enable_pin, dco_pin, step_timer, step_channel, accel_timer, accel_ch, name)
        self.ENABLED = 0
        self.DONE = 1

    def mot_fun(self):
        '''
        Defines the Motor task method that runs repeatedly.
        '''
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)

        self.state = STATE_1

        while True:
            ## STATE 1: IDLE
            if self.state == STATE_1:
                self.check_disable()
                if self.params.any() and self.ENABLED:
                    self.Motor.set_direction(self.params.get()[1])
                    self.Motor.set_init_speed(self.params.get()[2])
                    self.Motor.set_max_speed(self.params.get()[3])
                    self.Motor.set_accel_rate(self.params.get()[4])
                    self.Motor.move_to(self.params.get()[0])
                    self.DONE = 0
                    self.state = STATE_2
                self.status.put(self.DONE)

            ## STATE 2: MOVING
            elif self.state == STATE_2:
                self.check_disable()
                if self.Motor.is_done() or abs(self.limit.get()) or not self.ENABLED:
                    self.Motor.stop()
                    self.DONE = 1
                    self.state = STATE_1
                self.status.put(self.DONE)

            yield(self.state)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def check_disable(self):
        '''
        '''
        if not self.enable.get():
            self.Motor.disable_motor()
            self.ENABLED = 0
        else:
            self.Motor.enable_motor()
            self.ENABLED = 1
