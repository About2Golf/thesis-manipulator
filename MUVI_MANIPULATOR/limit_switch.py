import pyb
import micropython
import machine

class Limit_Switch:
    '''
    This is the class definition for a pair of plus and minus limit switches.
    '''

    def __init__ (self, pin_minus, pin_plus, name):
        '''
        The initialization method for the limit switches.
        @param pin_minus - The negative coordinate limit switch pin
        @param pin_plus - The positive coordinate limit switch pin
        @param name - The name of the stage ('X' or 'Z' or 'Y' or 'P')
        '''
        self.pin_m = machine.Pin(pin_minus, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin_p = machine.Pin(pin_plus, machine.Pin.IN, machine.Pin.PULL_UP)
        self.name = name
        string = self.name + 'Limit Switch Successfully Initialized'
        print (string)

    def read_limit(self):
        '''
        This method returns the values of the diagnostics pins.
        @return The status of the limit switches
        '''
        if not self.pin_m.value():
            return -1
        elif not self.pin_p.value():
            return 1
        else:
            return 0
