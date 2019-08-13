#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 00:52:43 2018

@author: JasonGrillo
"""

import pyb
import micropython

class Nerf_Task:
    ''' This defines the task function method for a nerf gun.
    '''
    
    def __init__(self, WINDUP_GUN, FEED_BULLETS, pin1, pin2):
        ''' Construct an encoder task function by initilizing any shared
            variables and initialize the encoder object
            @param WINDUP_GUN The shared variable flag indicating when to windup shooting motors
            @param FEED_BULLETS The shared variable flag indicating when to shoot bullets
            @param pin1 The motor windup pin (connected to mosfet)
            @param pin2 The bullet feeder pin (connected to mosfet)
        '''
        self._WINDUP_GUN = WINDUP_GUN
        self._FEED_BULLETS = FEED_BULLETS
        self._pin1 = pin1
        self._pin2 = pin2
        
    def gun_fun(self):
        ''' Defines the task function method for an NERF GUN object.
        '''
        WindUp_Pin = pyb.Pin(self._pin1, pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP) 
        Fire_Pin = pyb.Pin(self._pin2, pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)     
        
        STATE_0 = micropython.const(0)
        STATE_1 = micropython.const(1)
        STATE_2 = micropython.const(2)
        
        self.state = STATE_0
        
        while True:        
            ## STATE 0: NOT WINDUP AND NOT SHOOT    
            if self.state == STATE_0:
                WindUp_Pin.low()
                Fire_Pin.low()
                if self._WINDUP_GUN.get():
                    WindUp_Pin.high()
                    self.state = STATE_1
            
            ## STATE 1: WINDUP AND NOT SHOOT
            elif self.state == STATE_1:
                if not self._WINDUP_GUN.get() and not self._FEED_BULLETS.get():
                    WindUp_Pin.low()
                    Fire_Pin.low()
                    self.state = STATE_0
                elif self._WINDUP_GUN.get() and self._FEED_BULLETS.get():
                    WindUp_Pin.high()
                    Fire_Pin.high()
                    self.state = STATE_2
                
            ## STATE 2: WINDUP AND SHOOT
            elif self.state == STATE_2:
                if not self._WINDUP_GUN.get() and not self._FEED_BULLETS.get():
                    WindUp_Pin.low()
                    Fire_Pin.low()
                    self.state = STATE_0
                elif self._WINDUP_GUN.get() and not self._FEED_BULLETS.get():
                    Fire_Pin.low()
                    self.state = STATE_1
                
            yield (self.state)