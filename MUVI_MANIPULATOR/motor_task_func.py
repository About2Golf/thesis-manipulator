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
    The class definition for a stepper motor task. The motor task handles the
    motor commands for a linear or rotary stage.
    '''

    def __init__(self, params_queue, steps_queue, enable_share, status_share,
                    limit_share, step_pin, dir_pin, enable_pin, dco_pin,
                        step_timer, step_channel, accel_timer, accel_ch, name):
        ''' The initialization method for a stepper motor.
            @param params_queue - The motion profile Queue
            @param steps_queue - The completed steps Queue
            @param enable_share - The enable command Share
            @param status_share - The motion status Share
            @param limit_share - The limit switch status Share
            @param step_pin - The step pin
            @param dir_pin - The direction pin
            @param enable_pin - The enable pin
            @param dco_pin - The DC step pin
            @param step_timer - The step generating timer
            @param step_channel - The step generator channel specific to the stage
            @param accel_timer - The ramp acceleration timer
            @param accel_ch - The ramp acceleration channel specific to the stage
            @param name - The name of the stage ('X' or 'Z' or 'Y' or 'P')
        '''
        self.params = params_queue
        self.steps = steps_queue
        self.enable = enable_share
        self.status = status_share
        self.limit = limit_share
        self.Motor = motor.TMC2160Driver(step_pin, dir_pin, enable_pin, dco_pin, step_timer, step_channel, accel_timer, accel_ch, name)
        self.ENABLED = 0
        self.DONE = 1
        self.limit_counter = 0
        self.name = name

    def mot_fun(self):
        '''
        Defines the Motor task state machine that is repeatedly called.
        '''
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)

        self.state = STATE_1

        while True:
            ## STATE 1: IDLE
            if self.state == STATE_1:
                self.check_disable()
                if self.params.any() and self.ENABLED:
                    self.Motor.set_direction(int(self.params.get()))
                    self.Motor.set_init_speed(int(self.params.get()))
                    self.Motor.set_max_speed(int(self.params.get()))
                    self.Motor.set_accel_rate(int(self.params.get()))
                    self.Motor.move_to(int(self.params.get()))
                    self.DONE = 0
                    self.limit_counter = 0
                    self.state = STATE_2
                self.status.put(self.DONE)

            ## STATE 2: MOVING
            elif self.state == STATE_2:
                self.check_disable()
                self.limit_counter += 1
                if (self.limit_counter > 400 and abs(self.limit.get())) or not self.ENABLED:
                    self.Motor.stop()
                    self.steps.put(self.Motor.get_steps_moved())
                    self.DONE = 1
                    self.state = STATE_1
                elif self.Motor.is_done():
                    self.steps.put(self.Motor.get_steps_moved())
                    self.DONE = 1
                    self.state = STATE_1
                self.status.put(self.DONE)

            yield(self.state)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def check_disable(self):
        '''
        This method sets the motor enable status that is commanded from the GUI.
        '''
        if not self.enable.get():
            self.Motor.disable_motor()
            self.ENABLED = 0
        else:
            self.Motor.enable_motor()
            self.ENABLED = 1
