# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 13:40:31 2016

Objects to interface with Velmex VXM controllers. Unit agnostic.

@author: Van Shourt


-----
updated Python 3
downgraded again to Python 2

"""
#import time
import serial

class vxm_axis3:
    """Axis sub-object for VXM controller"""

    def __init__(self, steps_per_rev, screw_pitch,num_axes):
        """Screw pitch can be in any unit"""
        # Remember that pitch is NOT threads per inch!
        self.stepsVal = steps_per_rev
        self.pitchVal = screw_pitch
        print "VXM: Axis Initialized ",num_axes
        
    def pitch(self):
        return self.pitchVal
        
    def steps(self):
        return self.stepsVal
        
    # Maybe sanitize the inputs at some point? 
    # I hate that we can't use private variables. This is why we can't have nice things.
        
    def setPitch(self, screw_pitch):
        self.pitchVal = screw_pitch
        
    def setSteps(self, steps_per_rev):
        self.stepsVal = steps_per_rev
        
        
        

class vxm_controller3:
    """Allows convenient interfacing with a Velmex VXM controller (or array)"""
    
    def __init__(self, com_port, num_axes):
        self.serialCom = serial.Serial(port='COM' + str(com_port), baudrate=9600,parity=serial.PARITY_NONE,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE, timeout=1)
#        print self.serialCom
        self.port = com_port
        
        if num_axes > 4:
            print 'VXM: Axes count exceeds limit of 4.'
            return None
            
        self.axes = []
            
        for x in range(1,num_axes+1):
            self.axes.append(vxm_axis3(400,0.1,x)) # Defaults set for DESI Grating Efficiency Rig
            
        print 'VXM: Device Initialized: COM' + str(com_port)
            
            
    def send_command(self,command_string, wait_for_completion = True, debug = False):
        """Sends direct serial commands and returns serial response"""
        if (debug):
            print 'VXM: Sent: ' + command_string
        self.serialCom.flushInput()
        self.serialCom.write(command_string)
        response_string = ""
        if wait_for_completion == True:
            while (response_string == ""):
                response_string = self.serialCom.readline()
            if (debug):
                print 'VXM: Recd: ' + response_string
                
            return response_string
        return response_string
    
    def close(self):
        self.serialCom.close()
        print 'VXM: Device Closed'
        
        
    def reconnect(self):
        if self.serialCom.closed == True:
            self.serialCom = serial.Serial(port='COM' + str(self.port), baudrate=9600,parity=serial.PARITY_NONE,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE, timeout=1)
        
            
    def home_axis(self, axis_to_home):
        """Requires limit switch"""
        self.send_command('F,C,K,S' + str(axis_to_home) + 'M2000,I' + str(axis_to_home) + 'M0,I' + str(axis_to_home) + 'M-50,IA' + str(axis_to_home) + 'M-0,R')
      
    def set_home(self, axis_to_home):
        """Requires limit switch"""
        self.send_command('F,C,K,IA' + str(axis_to_home) + 'M-0,R')

      
    def get_location(self, axis_to_read):
        if axis_to_read == 1:
            command_string = 'X'
        elif axis_to_read == 2:
            command_string = 'Y'
        elif axis_to_read == 3:
            command_string = 'Z'
        elif axis_to_read == 4:
            command_string = 'T'
        else:
            print 'VXM: Invalid Axis'
            return None
        
        
        readout = ''.join(c for c in self.send_command(command_string) if c.isdigit())
        #print 'CHECK: ' +readout #+ self.send_command(command_string)
        return float(readout)
        #return #int(self.send_command(command_string))
        
        
    def absoluteMove(self, axis_to_move, move_speed, destination, backlash = 30,TOWAIT=True):
        """Move to absolute location in units (e.g. inches)
        Backlash is in steps"""
        current_location = self.get_location(axis_to_move)
        steps_factor = (self.axes[axis_to_move-1].steps()/self.axes[axis_to_move-1].pitch())
        destination_steps = destination * -steps_factor # Negative due to limit switch location
        speed_steps = move_speed * steps_factor
        
        command_string = 'F,C,K,S' + str(axis_to_move) + 'M' + str(speed_steps) + ',IA' + str(axis_to_move)
        
        if (destination_steps > current_location) and (backlash > 0):
            command_string = command_string + 'M' + str(destination_steps + backlash) + ',IA' + str(axis_to_move)
        elif (destination_steps < current_location) and (backlash < 0):
            command_string = command_string + 'M' + str(destination_steps + backlash) + ',IA' + str(axis_to_move)
            
        command_string = command_string + 'M' + str(destination_steps) + ',R'
        
        self.send_command(command_string,wait_for_completion=TOWAIT)

    def absoluteMoveSteps(self,axis_to_move, move_speed, destination, backlash = 30):
        """Move to absolute location in motor steps"""
        current_location = self.get_location(axis_to_move)
        destination_steps = -destination # Negative due to limit switch location
        speed_steps = move_speed
        
        command_string = 'F,C,K,S' + str(axis_to_move) + 'M' + str(speed_steps) + ',IA' + str(axis_to_move)
        
        if (destination_steps > current_location) and (backlash > 0):
            command_string = command_string + 'M' + str(destination_steps + backlash) + ',IA' + str(axis_to_move)
        elif (destination_steps < current_location) and (backlash < 0):
            command_string = command_string + 'M' + str(destination_steps + backlash) + ',IA' + str(axis_to_move)
            
        command_string = command_string + 'M' + str(destination_steps) + ',R'
        
        self.send_command(command_string)
        
