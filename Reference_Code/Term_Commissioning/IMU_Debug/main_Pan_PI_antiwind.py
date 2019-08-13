"""
Created on Thu Jan 25 19:31:26 2018

@author: Jason Grillo, Thomas Goehring, Trent Peterson
"""

#Yellow Encoder Cable: B7
#Gray Encoder Cable: B6
 
import pyb
import motor
import controller
import utime
import micropython
import encoder

# Create all objects 
Encoder_1 = encoder.Encoder(4, pyb.Pin.board.PB6, pyb.Pin.board.PB7)
DC_Motor_1 = motor.MotorDriver(3,pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5)
Controller_1 = controller.Controller(0.019,0.0003) ####

# Setup/Initialization
def setup():
    ''' This initializes the encoder and motor to zero values. '''
    Encoder_1.zero_encoder()   #
    DC_Motor_1.set_duty_cycle(0)
    Controller_1.set_setpoint(1000)
    
# Continuous loop
def loop():
    ''' This is the main loop that handles the DC Motor step response
        functionality. '''      
    
    # Define the time to run the step response test (currently 1 second)
    count = 500 ###
    time = []
    position = []
    init_time = utime.ticks_ms()
    while(count>0):
        # Add current time to list of times
        time.append(utime.ticks_ms() - init_time)
        #Read current encoder value & store it in list of encoder vals
        current_enc_read = Encoder_1.read_encoder()
        #osition.append(current_IMU_read)
        # Use controller object to get appropriate duty cycle for motor
        Duty_Cycle_1 = Controller_1.repeatedly(current_enc_read)
        # Set duty cycle to motor
        DC_Motor_1.set_duty_cycle(Duty_Cycle_1)
        # Delay 10 ms.... Need to use interrupts and raise a flag later...
        print('Set Point: ' + str(Controller_1.setpoint) + '   Current Position:' + str(current_enc_read) + '   PWM: ' + str(Duty_Cycle_1) + '   Error: ' +str(Controller_1._error) + '   ESUM:' + str(Controller_1._esum))
        utime.sleep_ms(2)
        count -= 1
    # Turn off motor once test is complete
    DC_Motor_1.set_duty_cycle(0)
    # Print time and position data to the terminal
    print_lists(time,position)
    # Write time and position data to a csv file

# loop() ends here...
# -------------------------------------------------------------------------#

# Print the Time and Position
def print_lists(list1,list2):
    ''' Prints two columns to the terminal separated by commas. '''
    print('Ready to Plot')    
    print('Time[ms]' + ',' + 'Position[ticks]')
    for (time,position) in zip(list1,list2): # Referenced https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
        print(str(time) + ',' + str(position))
    #print(end = " ")
        
# --------------------------------------------------------------------------- #
#                                         Runs The Code
# --------------------------------------------------------------------------- #

setup()

while(1):
    print('Start of Loop') #
    setup()
    loop()
    avalue = input()  
    
    