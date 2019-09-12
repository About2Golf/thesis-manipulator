"""
Created on Fri Feb 16 16:53:17 2018

@privatesection - Stuff in this file doesn't need to be Doxygen-ed

@author: JasonGrillo
"""

import pyb
import micropython
import gc

import motor_task_func

import cotask
import task_share



# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
micropython.alloc_emergency_exception_buf (100)


# =========================================================================== #
# ======================== Run the Turret Code ============================== #
# =========================================================================== #

if __name__ == "__main__":

    ####################################################################
    ############################ VARIABLES #############################
    ####################################################################


    ####################################################################
    ########################## TASK OBJECTS ############################
    ####################################################################

    pwm1 = motor_task_func.Motor_Task(20, 1, 5, 3, pyb.Pin.board.PA2, 2)
    pwm2 = motor_task_func.Motor_Task(20, 1, 5, 4, pyb.Pin.board.PA3, 2)
    pwm3 = motor_task_func.Motor_Task(1, 20, 8, 2, pyb.Pin.board.PC8, 2)
    pwm4 = motor_task_func.Motor_Task(1, 20, 8, 1, pyb.Pin.board.PC6, 2)
    # pwm2 = motor_task_func.Motor_Task(500, 5, 1, 3, pyb.Pin.board.PB15, 1)

    ####################################################################
    ############################## TASKS ###############################
    ####################################################################

    #Turret Hub Timing => Timing: 100 ms, Priority 1 (Lowest)
    task0 = cotask.Task (pwm1.mot_fun, name = 'Task_0', priority = 1,
                         period = 100, profile = True, trace = False)
    task1 = cotask.Task (pwm2.mot_fun, name = 'Task_1', priority = 1,
                         period = 100, profile = True, trace = False)
    task2 = cotask.Task (pwm3.mot_fun, name = 'Task_2', priority = 1,
                         period = 100, profile = True, trace = False)
    task3 = cotask.Task (pwm4.mot_fun, name = 'Task_3', priority = 1,
                         period = 100, profile = True, trace = False)
    #Pan Encoder => Timing 2 ms, Priority 5(Highest)
    # task1 = cotask.Task (pwm2.mot_fun, name = 'Task_1', priority = 5,
    #                      period = 100, profile = True, trace = False)


    cotask.task_list.append (task0)
    cotask.task_list.append (task1)
    cotask.task_list.append (task2)
    cotask.task_list.append (task3)
    # cotask.task_list.append (task1)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    ####################################################################
    ############################### RUN ################################
    ####################################################################

    # Run the scheduler with the chosen scheduling algorithm
    while True:
        cotask.task_list.pri_sched()
