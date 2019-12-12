"""
Created on Fri Feb  9 23:53:47 2018

@author: JasonGrillo
"""
import encoder
import limit_switch

import pyb
import micropython
import machine

class Feedback_Task:
    '''  The class definition for the feedback task. The feedback task
    handles the sensor hardware for the encoder and limit switches for both
    linear and rotary stages.
    '''

    def __init__(self, encoder_share, limit_share, zero_share, timer,
                        enc_A, enc_B, ls_pin_m, ls_pin_p, name):
        ''' The initialization method for a stage's feedback sensors.
            @param encoder_share - The shared variable between tasks that contains the encoder readings
            @param limit_share - The shared variable that contains the plus and minus limit switch readings
            @param zero_share - The command to zero the encoder
            @param timer - The encoder's timer channel
            @param enc_A - The encoder's first pin, Pin A
            @param enc_B - The encoder's second pin, Pin B
            @param ls_pin_m - The minus limit switch pin
            @param ls_pin_p - The plus limit switch pin
            @param name - The name of the stage ('X' or 'Z' or 'Y' or 'P')
        '''
        self.encoder_share = encoder_share
        self.limit_share = limit_share
        self.zero = zero_share
        self.Encoder = encoder.Encoder(timer, enc_A, enc_B, name)
        self.Limit = limit_switch.Limit_Switch(ls_pin_m, ls_pin_p, name)
        self.limit_val = 0
        self.prev_limit_val = 0
        self.encoder_val = 0
        self.prev_encoder_val = 0
        self.name = name

    def fb_fun(self):
        '''
        Defines the feedback task state machine that is repeatedly called.
        '''
        STATE_0 = micropython.const (0)
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)

        self.state = STATE_0

        while True:
            ## STATE 0: Initialize Limit Variables
            if self.state == STATE_0:
                self.limit_val = self.Limit.read_limit()
                self.prev_limit_val = self.limit_val
                self.state = STATE_1

            ## STATE 1: Send Feedback
            if self.state == STATE_1:
                self.limit_val = self.Limit.read_limit()
                self.encoder_val = self.Encoder.read_encoder()
                self.limit_share.put(self.limit_val)
                self.encoder_share.put(self.encoder_val)
                if self.zero.get():
                    self.state = STATE_2

            ## STATE 2: Zero Encoder
            elif self.state == STATE_2:
                self.Encoder.zero_encoder()
                self.zero.put(0)
                self.state = STATE_1

            yield(self.state)

    def limit_toggled(self):
        '''
        This method indicates whether or not a limit switch changed its state.
        '''
        if self.prev_limit_val == self.limit_val:
            return False
        else:
            return True
