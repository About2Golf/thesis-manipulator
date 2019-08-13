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
        
        self.TARGET_CMD = False
        self.CALIBRATION_I_DONE = False
        self.CALIBRATION_II_DONE = False
        self.CALIBRATION_III_DONE = False
        self.timeout = 1000
#        self.timer
        self.pan_rec = 0
        self.tilt_rec = 0
        self.I_location = [0.0, 0.0]
        self.II_location = [0.0, 0.0]
        self.III_location = [0.0, 0.0]
        self.pan_centroids = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.tilt_centroids = [0.0, 0.0, 0.0, 0.0, 0.0]
        
    def turret_hub_fun(self):
        ''' Defines the task function method for a turret hub object.
        '''
        vcp = pyb.USB_VCP ()
        
        STATE_0 = micropython.const(0)
        STATE_1 = micropython.const(1)
        STATE_2 = micropython.const(2)
        STATE_3 = micropython.const(3)
        STATE_4 = micropython.const(4)
        STATE_5 = micropython.const(5)
        
        self.state = STATE_0
        
        while True:        
            ## STATE 0: CALIBRATE GRID - POINT I   
            if self.state == STATE_0:  
                self.pan_coords.put(0)
                self.tilt_coords.put(0)
                
                if vcp.any(): 
                    self.GUI_input = float(vcp.read(2).decode('UTF-8'))
                    self.GUI_Lookup_Table(self.GUI_input)
                yield (self.state)
                
                if self.CALIBRATION_I_DONE:
                    self.state = STATE_1   
            
            ## STATE 1: CALIBRATE GRID - POINT II    
            elif self.state == STATE_1:
                if vcp.any(): 
                    self.GUI_input = float(vcp.read(2).decode('UTF-8'))
                    self.GUI_Lookup_Table(self.GUI_input)
                yield (self.state)
                
                if self.CALIBRATION_II_DONE:
                    self.state = STATE_2
            
            ## STATE 2: CALIBRATE GRID - POINT III
            elif self.state == STATE_2:
                if vcp.any(): 
                    self.GUI_input = float(vcp.read(2).decode('UTF-8'))
                    self.GUI_Lookup_Table(self.GUI_input)
                yield (self.state)
                
                if self.CALIBRATION_III_DONE:
                    self.pan_delta = (self.I_location[0] - self.II_location[0])/5
                    self.pan_centroids[0] = self.I_location[0] + self.pan_delta/2
                    self.pan_centroids[1] = self.pan_centroids[0] + self.pan_delta
                    self.pan_centroids[2] = self.pan_centroids[1] + self.pan_delta
                    self.pan_centroids[3] = self.pan_centroids[2] + self.pan_delta
                    self.pan_centroids[4] = self.pan_centroids[3] + self.pan_delta

                    self.tilt_delta = (self.II_location[1] - self.III_location[1])/5
                    self.tilt_centroids[0] = self.I_location[1] + self.pan_delta/2
                    self.tilt_centroids[1] = self.tilt_centroids[0] + self.pan_delta
                    self.tilt_centroids[2] = self.tilt_centroids[1] + self.pan_delta
                    self.tilt_centroids[3] = self.tilt_centroids[2] + self.pan_delta
                    self.tilt_centroids[4] = self.tilt_centroids[3] + self.pan_delta

                    print(self.pan_centroids)
                    print('\n')
                    print(self.tilt_centroids)
                    self.state = STATE_3
            
            ## STATE 3: STOPPED, NOT SHOOTING
            elif self.state == STATE_3:
                if vcp.any(): 
                    self.GUI_input = float(vcp.read(2).decode('UTF-8'))
                    self.GUI_Lookup_Table(self.GUI_input)
                yield (self.state)
                
                if self.TARGET_CMD:
                    self.WINDUP_GUN.put(1)
                    wind_time = utime.ticks_ms()
                    while (utime.ticks_ms() - wind_time) < 500:
                        yield (self.state)
                    self.FEED_BULLETS.put(1)
                    self.state = STATE_4

            ## STATE 4: MOVING, SHOOTING
            elif self.state == STATE_4:
                if self.pan_completion.get() > 50.0 and self.tilt_completion.get() > 50.0:
                    # init the time for keeping track of how long to shoot
                    self.timer_init = utime.ticks_ms()
                    # clear the target cmd flag for state 1 next time
                    self.TARGET_CMD = False
                    self.state = STATE_5
                    
            ## STATE 5: STOPPED, SHOOTING
            elif self.state == STATE_5:
                if (utime.ticks_ms() - self.timer_init) > self.timeout:
                    self.FEED_BULLETS.put(0)
                    # delay 1 second to wait for feeder to stop..
                    while (utime.ticks_ms() - self.timeout) < 1000:
                        yield (self.state)
                    self.WINDUP_GUN.put(0)
#                    self.timer_init = 0
                    self.state = STATE_3
                    
            yield (self.state)
                

    def GUI_Lookup_Table(self, command):
        ''' Decodes GUI commands based on a defined list of commands
        
        GUI Layout:
         _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
        | A1  B1  C1  D1  E1   Wind_on    Up      I_Location    |
        
        | A2  B2  C2  D2  E2   Feed_on    Down    II_Location   |
        
        | A3  B3  C3  D3  E3   Wind_off   Left    III_Location  |
        
        | A4  B4  C4  D4  E4   Feed_off   Right                 |
         
        | A5  B5  C5  D5  E5                                    |
         _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
         
         GUI Command Numbers:
         _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
        | 1   6   11  16  21      26      31          36        |
        
        | 2   7   12  17  22      27      32          37        |
        
        | 3   8   13  18  23      28      33          38        |
        
        | 4   9   14  19  24      29      34                    |
         
        | 5   10  15  20  25                                    |
         _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _         
         
        @param command The incoming GUI command to decode
        '''

# --- A TARGETS ---
        
       # A1 Target
        if(command == 1):
            self.pan_coords.put(self.pan_centroids[0]) 
            self.tilt_coords.put(self.tilt_centroids[0])
            self.TARGET_CMD = True
            
        # A2 Target
        elif(command == 2):
            self.pan_coords.put(self.pan_centroids[0]) 
            self.tilt_coords.put(self.tilt_centroids[1])
            self.TARGET_CMD = True

        # A3 Target
        elif(command == 3):
            self.pan_coords.put(self.pan_centroids[0]) 
            self.tilt_coords.put(self.tilt_centroids[2])  
            self.TARGET_CMD = True

        # A4 Target
        elif(command == 4):
            self.pan_coords.put(self.pan_centroids[0]) 
            self.tilt_coords.put(self.tilt_centroids[3]) 
            self.TARGET_CMD = True

        # A5 Target
        elif(command == 5):
            self.pan_coords.put(self.pan_centroids[0]) 
            self.tilt_coords.put(self.tilt_centroids[4]) 
            self.TARGET_CMD = True

# --- B TARGETS ---
            
        # B1 Target
        elif(command == 6):
            self.pan_coords.put(self.pan_centroids[1]) 
            self.tilt_coords.put(self.tilt_centroids[0])
            self.TARGET_CMD = True
            
        # B2 Target
        elif(command == 7):
            self.pan_coords.put(self.pan_centroids[1]) 
            self.tilt_coords.put(self.tilt_centroids[1])
            self.TARGET_CMD = True

        # B3 Target
        elif(command == 8):
            self.pan_coords.put(self.pan_centroids[1]) 
            self.tilt_coords.put(self.tilt_centroids[2])    
            self.TARGET_CMD = True

        # B4 Target
        elif(command == 9):
            self.pan_coords.put(self.pan_centroids[1]) 
            self.tilt_coords.put(self.tilt_centroids[3])   
            self.TARGET_CMD = True

        # B5 Target
        elif(command == 10):
            self.pan_coords.put(self.pan_centroids[1]) 
            self.tilt_coords.put(self.tilt_centroids[4])  
            self.TARGET_CMD = True

# --- C TARGETS ---
            
        # C1 Target
        elif(command == 11):
            self.pan_coords.put(self.pan_centroids[2]) 
            self.tilt_coords.put(self.tilt_centroids[0])
            self.TARGET_CMD = True
            
        # C2 Target
        elif(command == 12):
            self.pan_coords.put(self.pan_centroids[2]) 
            self.tilt_coords.put(self.tilt_centroids[1])
            self.TARGET_CMD = True

        # C3 Target
        elif(command == 13):
            self.pan_coords.put(self.pan_centroids[2]) 
            self.tilt_coords.put(self.tilt_centroids[2])   
            self.TARGET_CMD = True

        # C4 Target
        elif(command == 14):
            self.pan_coords.put(self.pan_centroids[2]) 
            self.tilt_coords.put(self.tilt_centroids[3])    
            self.TARGET_CMD = True

        # C5 Target
        elif(command == 15):
            self.pan_coords.put(self.pan_centroids[2]) 
            self.tilt_coords.put(self.tilt_centroids[4]) 
            self.TARGET_CMD = True             

# --- D TARGETS ---
            
        # D1 Target
        elif(command == 16):
            self.pan_coords.put(self.pan_centroids[3]) 
            self.tilt_coords.put(self.tilt_centroids[0])
            self.TARGET_CMD = True
            
        # D2 Target
        elif(command == 17):
            self.pan_coords.put(self.pan_centroids[3]) 
            self.tilt_coords.put(self.tilt_centroids[1])
            self.TARGET_CMD = True

        # D3 Target
        elif(command == 18):
            self.pan_coords.put(self.pan_centroids[3]) 
            self.tilt_coords.put(self.tilt_centroids[2]) 
            self.TARGET_CMD = True

        # D4 Target
        elif(command == 19):
            self.pan_coords.put(self.pan_centroids[3]) 
            self.tilt_coords.put(self.tilt_centroids[3]) 
            self.TARGET_CMD = True

        # D5 Target
        elif(command == 20):
            self.pan_coords.put(self.pan_centroids[3]) 
            self.tilt_coords.put(self.tilt_centroids[4])  
            self.TARGET_CMD = True
            
# --- E TARGETS ---
            
        # E1 Target
        elif(command == 21):
            self.pan_coords.put(self.pan_centroids[4]) 
            self.tilt_coords.put(self.tilt_centroids[0])
            self.TARGET_CMD = True
            
        # E2 Target
        elif(command == 22):
            self.pan_coords.put(self.pan_centroids[4]) 
            self.tilt_coords.put(self.tilt_centroids[1])
            self.TARGET_CMD = True

        # E3 Target
        elif(command == 23):
            self.pan_coords.put(self.pan_centroids[4]) 
            self.tilt_coords.put(self.tilt_centroids[2])    
            self.TARGET_CMD = True

        # E4 Target
        elif(command == 24):
            self.pan_coords.put(self.pan_centroids[4]) 
            self.tilt_coords.put(self.tilt_centroids[3])    
            self.TARGET_CMD = True

        # E5 Target
        elif(command == 25):
            self.pan_coords.put(self.pan_centroids[4]) 
            self.tilt_coords.put(self.tilt_centroids[4])   
            self.TARGET_CMD = True

# --- SHOOT ---
        
        # WINDUP ON
        elif(command == 26):
            self.WINDUP_GUN.put(1)       

        # FEED ON
        elif(command == 27):
            self.FEED_BULLETS.put(1)           
        
        # WINDUP OFF
        elif(command == 28):
            self.WINDUP_GUN.put(0)       

        # FEED OFF
        elif(command == 29):
            self.FEED_BULLETS.put(0) 
            
# --- MOVE ---
        
        # UP
        elif(command == 31):
            self.tilt_coords.put(self.tilt_angle.get() + 15)
            
        # DOWN
        elif(command == 32):
            self.tilt_coords.put(self.tilt_angle.get() - 15)
            
        # LEFT
        elif(command == 33):
            self.pan_coords.put(self.pan_position.get() + 1000)
            
        # RIGHT
        elif(command == 34):
            self.pan_coords.put(self.pan_position.get() - 1000)

# --- CALIBRATE LOCATIONS ---
        
        # I LOCATION
        elif(command == 36):
            self.I_location [0] = self.pan_position.get()
            self.I_location [1] = self.tilt_angle.get()
            self.CALIBRATION_I_DONE = True
            
        # II LOCATION
        elif(command == 37):
            self.II_location [0] = self.pan_position.get()
            self.II_location [1] = self.tilt_angle.get()
            self.CALIBRATION_II_DONE = True
            
        # III LOCATION
        elif(command == 38):
            self.III_location [0] = self.pan_position.get()
            self.III_location [1] = self.tilt_angle.get() 
            self.CALIBRATION_III_DONE = True