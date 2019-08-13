# -*- coding: utf-8 -*-
#
## @privatesection - Stuff in this file doesn't need to be Doxygen-ed
#
#  @author jr

import pyb
import micropython
import gc

import encoder
import motor
import controller
import utime

import cotask
import task_share
import print_task

# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
micropython.alloc_emergency_exception_buf (100)


STATE_0 = const (0)
STATE_1 = const (1)
STATE_2 = const (2)

#motor 1 times and positions
times_1 = []
positions_1 = []

#motor 2 times and positions
times_2 = []
positions_2 = []

def Encoder1_fun ():
    ''' Function which runs for Task 1, which toggles twice every second in a
    way which is only slightly silly.  '''    
    state = STATE_0
    while True:        
######### STATE 0: Initialize Encoder ###################################        
        if state == STATE_0:  
            # Init state        
            Encoder_1  = encoder.Encoder(4,pyb.Pin.board.PB6,pyb.Pin.board.PB7)
            state = STATE_1
######### STATE 1: Zero Encoder for Step Response #######################
        elif state == STATE_1:
            # Read encoder and update the shared variable              
            Encoder_1.zero_encoder()
            state = STATE_2
            
######### STATE 2: Get Encoder Values ##################################
        elif state == STATE_2:
            if Run.get():
                # Read encoder and update the shared variable
                enc_1_position.put(Encoder_1.read_encoder())
            else:
                state == STATE_1
        yield (state)



def MotorCtrl1_fun ():
    ''' Function which runs for Task 1, which toggles twice every second in a
    way which is only slightly silly.  '''
    
    state = STATE_0   
   
    while True:

##################STATE 0: INIT################################
        
        if state == STATE_0:  
            # Init state: create objects and stop motor
            DC_Motor_1 = motor.MotorDriver(3, pyb.Pin.board.PA10, pyb.Pin.board.PB4, pyb.Pin.board.PB5)
            Controller_1 = controller.Controller(.019,20000)            
            #Run.put(1) ###############################################for testinh
            state = STATE_1

##################STATE 1: WAIT FOR RUN################################
            
        elif state == STATE_1:  
            # Wait for Step Response: stops motor, if it runs, set count and change state 
            DC_Motor_1.set_duty_cycle(0)               
            if Run.get() == 1:                 
                count = 100
                init_time = utime.ticks_ms()
                state = STATE_2  

##################STATE 2: STEP RESPONSE################################
            
        elif state == STATE_2:  
             # Define the time to run the step response test (currently 1 second)           
            if count>0:
                # Add current time to list of times
                times_1.append(utime.ticks_ms() - init_time)
                # Read current encoder value & store it in list of encoder vals
                positions_1.append(enc_1_position.get())
                # Use controller object to get appropriate duty cycle for motor
                Duty_Cycle_1 = Controller_1.repeatedly(enc_1_position.get())
                # Set duty cycle to motor
                DC_Motor_1.set_duty_cycle(Duty_Cycle_1)                            
                count -= 1
                # Turn off motor once test is complete
            else:
                Run.put(0)
                state = STATE_1
        yield()
            
def Encoder2_fun ():
    ''' Function which runs for Task 1, which toggles twice every second in a
    way which is only slightly silly.  '''    
    state = STATE_0
    while True:        
######### STATE 0: Initialize Encoder ###################################        
        if state == STATE_0:  
            # Init state        
            Encoder_2  = encoder.Encoder(8,pyb.Pin.board.PC6,pyb.Pin.board.PC7)
            state = STATE_1
######### STATE 1: Zero Encoder for Step Response #######################
        elif state == STATE_1:
            # Read encoder and update the shared variable              
            Encoder_2.zero_encoder()
            state = STATE_2
######### STATE 2: Get Encoder Values ##################################
        elif state == STATE_2:
            if Run.get():
                # Read encoder and update the shared variable
                enc_2_position.put(Encoder_2.read_encoder())
            else:                
                state == STATE_1
        yield (state)


def MotorCtrl2_fun ():
    ''' Function which runs for Task 1, which toggles twice every second in a
    way which is only slightly silly.  '''
    
    state = STATE_0   
   
    while True:

##################STATE 0: INIT################################
        
        if state == STATE_0:  
            # Init state: create objects and stop motor
            DC_Motor_2 = motor.MotorDriver(5, pyb.Pin.board.PC1, pyb.Pin.board.PA0, pyb.Pin.board.PA1)
            Controller_2 = controller.Controller(.019,10000)            
            #Run.put(1) ###############################################for testinh
            state = STATE_1

##################STATE 1: WAIT FOR RUN################################
            
        elif state == STATE_1:  
            # Wait for Step Response: stops motor, if it runs, set count and change state 
            DC_Motor_2.set_duty_cycle(0)               
            if Run.get() == 1:                 
                count = 75
                init_time = utime.ticks_ms()
                state = STATE_2  

##################STATE 2: STEP RESPONSE################################
            
        elif state == STATE_2:  
             # Define the time to run the step response test (currently 1 second)           
            if count>0:
                # Add current time to list of times
                times_2.append(utime.ticks_ms() - init_time)
                # Read current encoder value & store it in list of encoder vals
                positions_2.append(enc_2_position.get())
                # Use controller object to get appropriate duty cycle for motor
                Duty_Cycle_2 = Controller_2.repeatedly(enc_2_position.get())
                # Set duty cycle to motor
                DC_Motor_2.set_duty_cycle(Duty_Cycle_2)                            
                count -= 1
                # Turn off motor once test is complete
            else:
                Run.put(0)
                state = STATE_1
        yield()

def UI_fun ():
    state = 0
    while True:
        if state == 0:  
            # Init state
            vcp = pyb.USB_VCP ()
            state = 1
        elif state == 1:            
            # Check for incoming characters and select motor run
            if vcp.any():             
                Run.put(1)                
                # Empty the comm port buffer of the character(s) just pressed                
                vcp.read()
                state = 2
        elif state == 2:            
            # Wait for step response to be done and then print the data
            if not Run.get():                
                # print the data
                print('\n\nMOTOR 1:')    
                print('Time[ms]' + ',' + 'Position[ticks]')
                for (time,position) in zip(times_1,positions_1): # Referenced https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
                    print(str(time) + ',' + str(position))                     
                    yield(state)
                
                print('\n\nMOTOR 2:')    
                print('Time[ms]' + ',' + 'Position[ticks]')
                for (time,position) in zip(times_2,positions_2): # Referenced https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
                    print(str(time) + ',' + str(position))                     
                    yield(state)
                
                # reinitialize the time and position array
                # https://stackoverflow.com/questions/850795/different-ways-of-clearing-lists                
                times_1[:] = []
                positions_1[:] = []
                state = 1
                print_diagnostics()
        yield (state)

def print_diagnostics():
    # Print a table of task data and a table of shared information data
    print ('\n' + str (cotask.task_list) + '\n')
    print (task_share.show_all ())
    print (task1.get_trace ())
    print ('\r\n')
    

# =============================================================================

if __name__ == "__main__":




    print ('\033[2JTesting scheduler in cotask.py\n')

    # Create a share and some queues to test diagnostic printouts
#    share0 = task_share.Share ('i', thread_protect = False, name = "Share_0")
#    q0 = task_share.Queue ('B', 6, thread_protect = False, overwrite = False,
#                           name = "Queue_0")
#    q1 = task_share.Queue ('B', 8, thread_protect = False, overwrite = False,
#                           name = "Queue_1")
    enc_1_position = task_share.Share ('i', thread_protect = False, name = "Share_0_enc_1_position")
    enc_2_position = task_share.Share ('i', thread_protect = False, name = "Share_0_enc_2_position")    
    Run = task_share.Share('i', thread_protect = False, name = "Run_Intertask_Comm_Variable")
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task (Encoder1_fun, name = 'Task_1', priority = 5, 
                         period = 2, profile = True, trace = False)
    task2 = cotask.Task (MotorCtrl1_fun, name = 'Task_2', priority = 3, 
                         period = 20, profile = True, trace = False)
    task3 = cotask.Task (Encoder2_fun, name = 'Task_3', priority = 5, 
                         period = 2, profile = True, trace = False)
    task4 = cotask.Task (MotorCtrl2_fun, name = 'Task_4', priority = 3, 
                         period = 20, profile = True, trace = False)
    task5 = cotask.Task (UI_fun, name = 'Task_5', priority = 1, 
                         period = 50, profile = True, trace = False)
    
    cotask.task_list.append (task1)
    cotask.task_list.append (task2)
    cotask.task_list.append (task3)
    cotask.task_list.append (task4)
    cotask.task_list.append (task5)

    # A task which prints characters from a queue has automatically been
    # created in print_task.py; it is accessed by print_task.put_bytes()

    # Create a bunch of silly time-wasting busy tasks to test how well the
    # scheduler works when it has a lot to do
#    for tnum in range (10):
#        newb = busy_task.BusyTask ()
#        bname = 'Busy_' + str (newb.ser_num)
#        cotask.task_list.append (cotask.Task (newb.run_fun, name = bname, 
#            priority = 0, period = 400 + 30 * tnum, profile = True))

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if any 
    # character is sent through the serial por
#    vcp = pyb.USB_VCP ()200
#    while not vcp.any ():
#        cotask.task_list.pri_sched ()
#
#    # Empty the comm port buffer of the character(s) just pressed
#    vcp.read ()

    while True:
        cotask.task_list.pri_sched()


