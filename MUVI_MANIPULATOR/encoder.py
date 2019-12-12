import pyb
import micropython
import machine

class Encoder:
    '''
    This is the hardware class definition for an encoder. It utilizes the
    STM32 quadrature encoder timer counter to keep track of the encoder position.
    '''

    def __init__ (self, timer, enc_A, enc_B, name):
        '''
        Initializes the pins and timer channels for an encoder object.
        @param timer - Specifies the timer for the encoder
        @param enc_A - First pin (A) used to read the encoder
        @param enc_B - Second pin (B) used to read the encoder
        @param name - The name of the stage ('X' or 'Z' or 'Y' or 'P')
        ''']
        ## First encoder pin associated with the pin1 (A) input parameter
        self.pin_object_1 = pyb.Pin(enc_A)
        ## Second encoder pin associated with the pin2 (B) input parameter
        self.pin_object_2 = pyb.Pin(enc_B)
        ## Timer number associated with the assigned pins
        self.timer_val = pyb.Timer(timer)
        ## Timer number associated with the assigned pins (Set timer to have one count per encoder count and a period of 65535)
        self.timer_val.init(prescaler=0,period=0xFFFF)
        ## Initializes channel 1 for pin1 (A) timer input
        self.ch1 = self.timer_val.channel(1,pyb.Timer.ENC_AB,pin=self.pin_object_1)
        ## Initializes channel 2 for pin2 (B) timer input
        self.ch2 = self.timer_val.channel(2,pyb.Timer.ENC_AB,pin=self.pin_object_2)
        # Instantaneous encoder reading at time of call
        self.__current_count = 0
        # Difference between last count and current count
        self.__delta_count = 0
        # Encoder reading from previous call
        self.__last_count = 0
        # Current absolute position of the encoder
        self.__encoder_val = 0
        self.name = name
        string = self.name + 'Encoder Successfully Initialized'
        print (string)

    def read_encoder(self):
        '''
        Reads the current encoder value
        @return encoder_val
        '''
        # Read current encoder count
        self.__current_count = self.timer_val.counter()
        # Subtract previous reading from current reading
        self.__delta_count = self.__current_count - self.__last_count
        # Account for 16-bit discontinuity phenomena
        if self.__delta_count > 32767:
           self.__delta_count -= 65535
        elif self.__delta_count < -32768:
            self.__delta_count += 65535
        # Add delta to absolute encoder position
        self.__encoder_val += self.__delta_count
        # Store current encoder reading into previous reading
        self.__last_count = self.__current_count
        #print(self.__encoder_val)
        return self.__encoder_val

    def zero_encoder(self):
        '''
        Resets all encoder parameters to zero
        @return encoder_val
        '''
        self.timer_val.counter(0)   # Reset all encoder parameters to zero
        self.__current_count = 0
        self.__last_count = 0
        self.__delta_count = 0
        self.__encoder_val = 0
        return self.__encoder_val

    def restore_encoder(self, restore_val):
        '''
        Restores the encoder to a previous state.
        @param restore_val - The encoder value to restore
        @return encoder_val
        '''
        self.__encoder_val = restore_val
        self.__last_count = restore_val
        self.timer_val.counter(restore_val)
        return self.__encoder_val
