import pyb
import machine

class Output_Pin:
    '''
    This class implements a limit switch object.
    '''

    def __init__ (self, opin, name):
        '''
        '''
        self.opin = machine.Pin(opin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        print('successfully created '+name)

    def set_high(self):
        '''
        This method returns the values of the diagnostics pins.
        @return pin_m The status of the limit minus Pin
        @return pin_p The status of the limit plus Pin
        '''
        self.opin.value(1)

    def set_low(self):
        '''
        This method returns the values of the diagnostics pins.
        @return pin_m The status of the limit minus Pin
        @return pin_p The status of the limit plus Pin
        '''
        self.opin.value(0)
