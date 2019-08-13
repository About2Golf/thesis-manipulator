import pyb

class Encoder:
    ''' This class implements a motor driver for the
    ME405 board. '''
    
    def __init__ (self, timer, pin1, pin2):
        ''' Initializes the pins and timer channels for an encoder object. 
        To create PB6 and PB7 Encoder reader:
            pin1 = "pyb.Pin.board.PB6"
            pin2 = "pyb.Pin.board.PB7"
            timer = "4"
        To create PC6 and PC7 Encoder reader:
            pin1 = "pyb.Pin.board.PC6"
            pin2 = "pyb.Pin.board.PC7"
            timer = "8"            
        @param timer: Specifies the timer for the encoder
        @param pin1: First pin (A) used to read the encoder
        @param pin2: Second pin (B) used to read the encoder  
        @return: Nothing.. just sets up the pins and timer channels
        '''
        print ('Creating an encoder') 
        ## Set Pin P#6 to encoder
        self.pin_object_1 = pyb.Pin(pin1)
        ## Set Pin P#7 to encoder
        self.pin_object_2 = pyb.Pin(pin2)
        ## Create a object timer based on P#6 and P#7 
        self.timer_val = pyb.Timer(timer)
        ## Set timer to have one count per encoder count and a period of 65535        
        self.timer_val.init(prescaler=0,period=0xFFFF)
        ## Set channel 1 to encoder mode       
        self.ch1 = self.timer_val.channel(1,pyb.Timer.ENC_AB,pin=self.pin_object_1)
        ## Set channel 2 to encoder mode  
        self.ch2 = self.timer_val.channel(2,pyb.Timer.ENC_AB,pin=self.pin_object_2)
        print('Encoder object successfully created')
        
    def read_encoder(self):
        ''' Reads the current encoder value
        @return: Current encoder value
        '''
        return self.timer_val.counter()
    
    def zero_encoder(self):
        ''' Resets the encoder to zero position
        @return: Nothing
        '''
        return 