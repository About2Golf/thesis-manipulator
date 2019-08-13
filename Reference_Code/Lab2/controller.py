"""
Created on Thu Jan 25 18:30:59 2018

@author: Jason Grillo, Thomas Goehring, Trent Peterson
"""

class Controller:
    ''' This class implements a generic proportional gain controller'''
    
    def __init__(self,Kp,setpoint):
        '''
        Initializes the proportional gain and defines the 
        initial setpoint for the controller.
        @param Kp: Sets proportional gain value
        @param setpoint: Sets initial setpoint value that is referenced by the controller

        '''
        print('Creating a controller')
        ## Proportional gain for a control loop
        self.Kp = Kp
        ## Desired output target  
        self.setpoint = setpoint
        ## Actuation signal sent to the plant
        self.__actuate_signal = 0
        ## Current output value of feedback from plant
        self.__current_value = 0
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
        
    def repeatedly(self,current_value):
        '''
        Method that repeatedly runs the control algorithm. Compares
        setpoint to actual signal value. This error is multiplied by
        the proportional gain and sent to the plant.
        @param current_value: Received current value from feedback loop
        @return actuate_signal: % duty cycle sent to device driver
        '''
        #Define current value variable to be used in control algorithm
        self.__current_value = current_value
        #Creates actuation signal from the proportional gain mulitplied by error
        self.__actuate_signal = (self.setpoint - self.__current_value)*self.Kp       
        return self.__actuate_signal