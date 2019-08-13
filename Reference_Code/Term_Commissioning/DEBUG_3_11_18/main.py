"""
Created on Thu Jan 25 19:31:26 2018

@author: Jason Grillo, Thomas Goehring, Trent Peterson
"""

#Yellow Encoder Cable: B7
#Gray Encoder Cable: B6
 
import pyb
import encoder
import utime

# Create all objects 
Encoder_1 = encoder.Encoder(4, pyb.Pin.board.PB6, pyb.Pin.board.PB7)

# Setup/Initialization
def setup():
    ''' This initializes the encoder and motor to zero values. '''
    Encoder_1.zero_encoder()   #
    
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

        # Delay 10 ms.... Need to use interrupts and raise a flag later...
        print('   Current Position:' + str(current_enc_read))
        utime.sleep_ms(2)
        count -= 1

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
    
    