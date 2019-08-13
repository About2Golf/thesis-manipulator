"""
Created on Thu Jan 18 2018

@author: mecha10, JGrillo, TGoehring, TPeterson
"""

class Encoder:
    ''' This class implements a motor driver for the
    ME405 board. '''
    
    def __init__ (self, pin1, pin2, timer):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. 
        To create PB6 and PB7 Encoder reader:
            pin1 = "PB6"
            pin2 = "PB7"
            timer = "4"
        To create PC6 and PC7 Encoder reader:
            pin1 = "PC6"
            pin2 = "PC7"
            timer = "8"            '''
        print ('Creating an encoder') 
        ## Set Pin P#6 to encoder
        self.pin_object_1 = pyb.Pin(pyb.Pin.board.pin1)
        ## Set Pin P#7 to encoder
        self.pin_object_2 = pyb.Pin(pyb.Pin.board.pin2)
        ## Create a object timer based on P#6 and P#7 
        timer_val = pyb.Timer(timer)
        ## Set timer to have one count per encoder count and a period of 65535        
        timer_val.init(prescaler=0,period=0xFFFF)
        ## Set channel 1 to encoder mode       
        self.ch1 = timer_val.channel(1,pyb.Timer.ENC_AB.pin=self.pin_object_1)
        ## Set channel 2 to encoder mode  
        self.ch2 = timer_val.channel(2,pyb.Timer.ENC_AB.pin=self.pin_object_2)
