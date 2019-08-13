"""
Created on Thu Jan 25 18:30:59 2018

@author: Jason Grillo, Thomas Goehring, Trent Peterson
"""
import utime

class Controller:
    ''' This class implements a generic proportional gain controller'''
    
    def __init__(self, Kp, Ki):
        '''
        Initializes the proportional gain and defines the 
        initial setpoint for the controller.
        @param Kp: Sets proportional gain value
        @param Ki: Sets integral gain value
        '''
        print('Creating a controller')
        ## Proportional gain for a control loop
        self.Kp = Kp
        ## Integral gain for a control loop
        self.Ki = Ki
        ## Desired output target variable
        self.setpoint = 0
        ## Actuation signal sent to the plant
        self.__actuate_signal = 0
        ## Current output value of feedback from plant
        self.__current_value = 0
        ## Set the start variable to true to begin integral gain term
        self.__start = True
        self._esum = 0
        
        print('Controller sucessfully created')

    def set_setpoint(self, new_setpoint):
        '''
        Method to enable the user to define a new setpoint that the
        control loop will use as a reference value.
        @param new_setpoint: User-defined setpoint that the controller uses as its reference value        
        '''
        self.setpoint = new_setpoint
        
    def set_Kp(self, new_Kp):
        '''
        Method to enable the user to define a new proportional gain
        that the control loop will use to multiply the error signal
        and output an actuation signal.
        @param new_Kp: User-defined propotional gain that is multiplied by error to produce and actuation signal         
        '''
        self.Kp = new_Kp
        
    def set_Ki(self, new_Ki):
        '''
        Method to enable the user to define a new proportional gain
        that the control loop will use to multiply the error signal
        and output an actuation signal.
        @param new_Kp: User-defined propotional gain that is multiplied by error to produce and actuation signal         
        '''
        self.Ki = new_Ki
        
    def repeatedly(self,current_value):
        '''
        Method that repeatedly runs the control algorithm. Compares
        setpoint to actual signal value. This error is multiplied by
        the proportional gain and sent to the plant.
        @param current_value: Received current value from feedback loop
        @return actuate_signal: % duty cycle sent to device driver
        '''
        if self.__start == True:
            self._previous_time = utime.ticks_ms()
            self.__start = False
        #Define current value variable to be used in control algorithm
        self.__current_value = current_value
        self._error = self.setpoint - self.__current_value
        # Calculate integral of error (Esum)
        self._del_t = utime.ticks_ms() - self._previous_time
        self._previous_time = utime.ticks_ms()
        if(self._error>0):
            if(self._esum < 4000):
                self._esum += self._error * self._del_t
        if(self._error<0):
            if(self._esum > -4000):
                self._esum += self._error * self._del_t              
        #Creates actuation signal from the proportional gain mulitplied by error
        self.__actuate_signal = self._error*self.Kp + self._esum*self.Ki
#        print(self.__actuate_signal)
        return self.__actuate_signal
    
    def percent_completion(self):
        ''' Returns the completion calculation for the controlled path.
        @return error The error from the desired position and current position
        '''
        if self.setpoint:
            return ((self._error/self.setpoint)*100)
        else:
            return 0;