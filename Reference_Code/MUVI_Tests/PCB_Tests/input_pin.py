import pyb
import machine

class Input_Pin:
    '''
    This class implements a limit switch object.
    '''

    def __init__ (self, ipin, name):
        '''
        '''
        self.ipin = machine.Pin(ipin, machine.Pin.IN, machine.Pin.PULL_UP)
        print('successfully created '+name)

    def read_pin(self):
        '''
        This method returns the values of the diagnostics pins.
        @return pin_m The status of the limit minus Pin
        @return pin_p The status of the limit plus Pin
        '''
        return (self.ipin.value())
