#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 00:00:39 2018

@author: JasonGrillo
"""

import pyb
import micropython
import utime

class Turret_Hub_Task:
    ''' This defines the task function method for a nerf turret hub.
    '''
    
    def __init__(self, pan_position, tilt_angle, pan_coords, tilt_coords, FEED_BULLETS, WINDUP_GUN, pan_completion, tilt_completion):
        ''' Construct a turret hub task function by initilizing any shared
            variables and objects
            @param pan_position The shared variable for the pan position
            @param tilt_angle The shared variable for the tilt position
            @param pan_coords The queue of coordinates for the pan axis
            @param tilt_coords The queue of coordinates for the tilt axis
            @param FEED_BULLETS The shared variable flag for the nerf gun shooting
            @param WINDUP_GUN The shared variable flag for the nerf gun motors
            @param pan_completion The shared variable for the pan axis completion percentage
            @param tilt_completion The shared variable for the tilt axis completion percentage
        '''
        self.pan_position = pan_position
        self.tilt_angle = tilt_angle
        self.pan_coords = pan_coords
        self.tilt_coords = tilt_coords
        self.FEED_BULLETS = FEED_BULLETS
        self.WINDUP_GUN = WINDUP_GUN
        self.pan_completion = pan_completion
        self.tilt_completion = tilt_completion
        
        self.TARGET_CMD = 0
        self.CALIBRATION_DONE = 1
        self.timeout = 1000
#        self.timer
        self.pan_rec = 0
        self.tilt_rec = 0
        
    def turret_hub_fun(self):
        ''' Defines the task function method for a turret hub object.
        '''
        vcp = pyb.USB_VCP ()
        
        STATE_0 = micropython.const(0)
        STATE_1 = micropython.const(1)
        STATE_2 = micropython.const(2)
        STATE_3 = micropython.const(3)
        STATE_4 = micropython.const(4)
        
        self.state = STATE_0
        
        while True:        
            ## STATE 0: CALIBRATE GRID    
            if self.state == STATE_0:  
                # --- insert calibration code here (waits for user input) ---
                # vars currently place holders for below code...
                self.pan_coords.put(0)
                self.tilt_coords.put(0)
                print('pan tilt to zero')
                yield (self.state)
                
                if self.CALIBRATION_DONE:
                    self.state = STATE_1
            
            ## STATE 1: STOPPED, NOT SHOOTING
            elif self.state == STATE_1:
                # --- insert XBee command code here (looking for cmds) ---
                # pull the coordinates from the pan and tilt matrices
                # set TARGET_CMD when coordinates are retrieved...
                #print('in first state')
                if vcp.any(): 
                    y = float(vcp.read(2).decode('UTF-8'))
                    print('recieved value:' + str(y))
                    if(y==1):
                        #self.coordinate.put(2000)     
                        self.pan_coords.put(2000) 
                        print('updtated pan coords to 2000')
                        self.TARGET_CMD = 1
                    if(y==2):
                        self.pan_coords.put(-2000) 
                        print('updtated pan coords to -2000')
                        self.TARGET_CMD = 1
                    if(y==3):
                        self.tilt_coords.put(15) 
                        print('updtated tilt coords to 15')
                        self.TARGET_CMD = 1
                    if(y==4):
                        self.tilt_coords.put(-15) 
                        print('updtated tilt coords to -15')
                        self.TARGET_CMD = 1
                    if(y==26):
                        self.WINDUP_GUN.put(1) 
                        print('WindUp On!')
                        self.TARGET_CMD = 1
                    if(y==27):
                        self.FEED_BULLETS.put(1) 
                        print('Fire On!')
                        self.TARGET_CMD = 1
                    if(y==28):
                        self.WINDUP_GUN.put(0) 
                        print('Wind Up Off')
                        self.TARGET_CMD = 1
                    if(y==29):
                        self.FEED_BULLETS.put(0)  
                        print('Fire Off')
                        self.TARGET_CMD = 1  
                    if(y==31):  
                        self.tilt_coords.put(self.tilt_angle.get()+15)  
                        print('Move Up')
                        print(self.tilt_angle.get()+15)
                        self.TARGET_CMD = 1
                    if(y==32):
                        self.tilt_coords.put(self.tilt_angle.get()-15) 
                        print('Move Down')
                        print(self.tilt_angle.get()-15)
                        self.TARGET_CMD = 1
                    if(y==33):
                        self.pan_coords.put(self.pan_position.get()+1000)  
                        print('Move Left')
                        self.TARGET_CMD = 1
                    if(y==34):
                        self.pan_coords.put(self.pan_position.get()-1000) 
                        
                        print('Move Right')
                        self.TARGET_CMD = 1    
                
                yield (self.state)
                
#                if self.TARGET_CMD:
##                    self.WINDUP_GUN.put(micropython.const(1))
##                    self.pan_coords.put(self.pan_coords)
##                    self.tilt_coords.put(self.tilt_coords)
#                    self.state = STATE_2
#                    
#            ## STATE 2: MOVING, NOT SHOOTING
#            elif self.state == STATE_2:
##                if self.pan_completion.get() > 50.0 and self.tilt_completion.get() > 50.0:
##                    self.FEED_BULLETS.put(micropython.const(1))
#                    self.state = STATE_3
#
#            ## STATE 3: MOVING, SHOOTING
#            elif self.state == STATE_3:
#                if self.pan_completion.get() == 100.0 and self.tilt_completion.get() == 100.0:
#                    # init the time for keeping track of how long to shoot
#                    self.timer_init = utime.ticks_ms()
#                    # clear the target cmd flag for state 1 next time
#                    self.TARGET_CMD = micropython.const(0)
#                    # clear the pan and tilt coords...
#                    self.pan_coords.put()
#                    self.tilt_coords.put()
#                    self.state = STATE_4
#                    
#            ## STATE 4: STOPPED, SHOOTING
#            elif self.state == STATE_4:
#                if (utime.ticks_ms() - self.timer_init) > self.timeout:
#                    self.FEED_BULLETS = micropython.const(0)
#                    # delay 1 second to wait for feeder to stop..
#                    while (utime.ticks_ms() - self.timeout) < 1000:
#                        yield (self.state)
#                    self.WINDUP_GUN = micropython.const(0)
##                    self.DESTINATION_50_COMPLETE = micropython.const(0)
#                    self.timer_init = 0
#                    self.state = STATE_1
#                    
#            yield (self.state)