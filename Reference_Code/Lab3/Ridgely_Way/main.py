## @privatesection - Stuff in this file doesn't need to be Doxygen-ed
#
#  @author Thomas Goehring, Jason Grillo, Trent Peterson

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

times_1 = []
positions_1 = [] 

times_2 = []
positions_2 = [] 


def Encoder1_fun ():
    ''' Blah blajh 
    '''    
    Encoder_1  = encoder.Encoder(4,pyb.Pin.board.PB6,pyb.Pin.board.PB7)
    state = 0
    while True:        
        if state == 0:  
            # Init state
            Encoder_1.zero_encoder()
            state = 1
        elif state == 1:
            if Run.get():
                # Read encoder and update the shared variable
                enc_1_position.put(Encoder_1.read_encoder())
            else:
                state = 0
        yield (state)

def MotorCtrl1_fun ():
    print('MOTOR1 STATE 0')
    
    # Init state: create objects and stop motor
    Motor_1 = motor.MotorDriver()
    # Controller takes inputs (Kp, setpoint)            
    Controller_1 = controller.Controller(.019,25000)     
    state = 0
    while True:      
        if state == 0:  
            Motor_1.set_duty_cycle(0)            
            if Run.get():            
                count = 115
                init_time = utime.ticks_ms()
                state = 1
        elif state == 1:               
            if count >= 0:
                # Add current time to list of times
                times_1.append(utime.ticks_ms() - init_time)
                # Add current encoder position to list of positions
                positions_1.append(enc_1_position.get())
                # Use controller object to get appropriate duty cycle for motor
                Duty_Cycle_1 = Controller_1.repeatedly(enc_1_position.get())
                # Set duty cycle to motor
                Motor_1.set_duty_cycle(Duty_Cycle_1)             
                count -= 1
            else:
                Run.put(0)                
                state = 0
        yield (state)
    
#def Encoder2_fun ():
#    ''' Blah blajh 
#    '''    
#    Encoder_2  = encoder.Encoder(8,pyb.Pin.board.PC6,pyb.Pin.board.PC7)
#    state = 0
#    while True:        
#        if state == 0:  
#            # Init state
#            Encoder_2.zero_encoder()
#            state = 1
#        elif state == 1:
#            if Run.get():
#                # Read encoder and update the shared variable
#                enc_2_position.put(Encoder_2.read_encoder())
#            else:
#                state = 0
#        yield (state)

#def MotorCtrl2_fun ():
#    print('MOTOR2 STATE 0')
#    # Init state: create objects and stop motor
#    Motor_2 = motor.MotorDriver()
#    # Controller takes inputs (Kp, setpoint)            
#    Controller_2 = controller.Controller(.019,37500)     
#    state = 0
#    while True:      
#        if state == 0:  
#            Motor_2.set_duty_cycle(0)            
#            if Run.get():            
#                count = 100
#                init_time = utime.ticks_ms()
#                state = 1
#        elif state == 1:               
#            if count >= 0:
#                # Add current time to list of times
#                times_2.append(utime.ticks_ms() - init_time)
#                # Add current encoder position to list of positions
#                positions_2.append(enc_2_position.get())
#                # Use controller object to get appropriate duty cycle for motor
#                Duty_Cycle_2 = Controller_2.repeatedly(enc_2_position.get())
#                # Set duty cycle to motor
#                Motor_2.set_duty_cycle(Duty_Cycle_2)             
#                count -= 1
#            else:
#                Run.put(0)                
#                state = 0
#        yield (state)


def UI_fun ():
    state = 0
    while True:
        if state == 0:  
            print('UI STATE 0')
            # Init state
            vcp = pyb.USB_VCP ()
            state = 1
        elif state == 1:
            print('UI STATE 1')
            
            # Check for incoming characters and select motor run
            if vcp.any():             
                Run.put(1)                
                # Empty the comm port buffer of the character(s) just pressed                
                vcp.read()
                state = 2
        elif state == 2:
            print('UI STATE 2')
            
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
        yield (state)

# =============================================================================

if __name__ == "__main__":
    # Create a share and some queues to test diagnostic printouts
    enc_1_position = task_share.Share ('i', thread_protect = False, name = "Share_0_enc_1_position")
    enc_2_position = task_share.Share ('i', thread_protect = False, name = "Share_0_enc_2_position")

    Run = task_share.Share('i', thread_protect = False, name = "Run_Intertask_Comm_Variable")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task (Encoder1_fun, name = 'Task_1', priority = 5, 
                         period = 1, profile = True, trace = False)
    task2 = cotask.Task (MotorCtrl1_fun, name = 'Task_2', priority = 3, 
                         period = 10, profile = True, trace = False)
#    task3 = cotask.Task (Encoder2_fun, name = 'Task_3', priority = 5, 
#                         period = 1, profile = True, trace = False)
#    task4 = cotask.Task (MotorCtrl2_fun, name = 'Task_4', priority = 3, 
#                         period = 10, profile = True, trace = False)
    task5 = cotask.Task (UI_fun, name = 'Task_5', priority = 3, 
                         period = 10, profile = True, trace = False)
    cotask.task_list.append (task1)
    cotask.task_list.append (task2)
#    cotask.task_list.append (task3)
#    cotask.task_list.append (task4)
    cotask.task_list.append (task5)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if any 
    # character is sent through the serial por
    while True:
        cotask.task_list.pri_sched ()