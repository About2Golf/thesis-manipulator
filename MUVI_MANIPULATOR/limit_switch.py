import pyb
import micropython
import machine

class Limit_Switch:
    '''
    This class implements a limit switch object.
    '''

    def __init__ (self, pin_minus, pin_plus, name):
        '''
        '''
        self.pin_m = machine.Pin(pin_minus, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin_p = machine.Pin(pin_plus, machine.Pin.IN, machine.Pin.PULL_UP)
        self.name = name
        print(self.name + 'Limit Switch Successfully Initialized')

    def read_limit(self):
        '''
        This method returns the values of the diagnostics pins.
        @return pin_m The status of the limit minus Pin
        @return pin_p The status of the limit plus Pin
        '''
        if self.pin_m.value():
            return -1
        elif self.pin_p.value():
            return 1
        else:
            return 0
