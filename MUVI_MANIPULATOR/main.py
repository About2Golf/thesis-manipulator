"""
Created on Fri Feb 16 16:53:17 2018
@privatesection - Stuff in this file doesn't need to be Doxygen-ed
@author: JasonGrillo
"""

import pyb
import micropython
import machine

import gc

import cotask
import task_share

import hub_task_func
import motor_task_func
import feedback_task_func


# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
micropython.alloc_emergency_exception_buf (100)

# =========================================================================== #
# =============================== Run the Code ============================== #
# =========================================================================== #

if __name__ == "__main__":

    ####################################################################
    ############################ VARIABLES #############################
    ####################################################################
    # Motor Parameters
    x_params = task_share.Queue ('f', 10, thread_protect = False,
                                   overwrite = False, name = "x_params")
    z_params = task_share.Queue ('f', 10, thread_protect = False,
                                   overwrite = False, name = "z_params")
    y_params = task_share.Queue ('f', 10, thread_protect = False,
                                   overwrite = False, name = "y_params")
    p_params = task_share.Queue ('f', 10, thread_protect = False,
                                   overwrite = False, name = "p_params")
    # Motor Parameters
    x_steps = task_share.Queue ('f', 5, thread_protect = False,
                                   overwrite = False, name = "x_steps")
    z_steps = task_share.Queue ('f', 5, thread_protect = False,
                                   overwrite = False, name = "z_steps")
    y_steps = task_share.Queue ('f', 5, thread_protect = False,
                                   overwrite = False, name = "y_steps")
    p_steps = task_share.Queue ('f', 5, thread_protect = False,
                                   overwrite = False, name = "p_steps")
    # Motor Positioning Status
    x_status = task_share.Share ('f', thread_protect = False,
                                     name = "x_status")
    z_status = task_share.Share ('f', thread_protect = False,
                                     name = "z_status")
    y_status = task_share.Share ('f', thread_protect = False,
                                     name = "y_status")
    p_status = task_share.Share ('f', thread_protect = False,
                                     name = "p_status")
    # Motor Enable
    x_enable = task_share.Share ('i', thread_protect = True,
                                     name = "x_enable")
    z_enable = task_share.Share ('i', thread_protect = True,
                                     name = "z_enable")
    y_enable = task_share.Share ('i', thread_protect = True,
                                     name = "y_enable")
    p_enable = task_share.Share ('i', thread_protect = True,
                                     name = "p_enable")
    # Encoder Value
    x_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "x_encoder")
    z_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "z_encoder")
    y_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "y_encoder")
    p_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "p_encoder")
    # Encoder Calibration
    x_zero = task_share.Share ('i', thread_protect = False,
                                     name = "x_zero")
    z_zero = task_share.Share ('i', thread_protect = False,
                                     name = "z_zero")
    y_zero = task_share.Share ('i', thread_protect = False,
                                     name = "y_zero")
    p_zero = task_share.Share ('i', thread_protect = False,
                                     name = "p_zero")
    # Limit Switch Value
    x_limit = task_share.Share ('i', thread_protect = False,
                                     name = "x_limit")
    z_limit = task_share.Share ('i', thread_protect = False,
                                     name = "z_limit")
    y_limit = task_share.Share ('i', thread_protect = False,
                                     name = "y_limit")
    p_limit = task_share.Share ('i', thread_protect = False,
                                     name = "p_limit")

    ####################################################################
    ########################## TASK OBJECTS ############################
    ####################################################################
    # Create Hub Task
    hub = hub_task_func.Hub_Task(x_params, z_params, y_params, p_params,
            x_steps, z_steps, y_steps, p_steps,
                x_status, z_status, y_status, p_status,
                    x_enable, z_enable, y_enable, p_enable,
                        x_encoder, z_encoder, y_encoder, p_encoder,
                            x_zero, z_zero, y_zero, p_zero,
                                x_limit, z_limit, y_limit, p_limit,
                                    pyb.Pin.board.PC10, pyb.Pin.board.PB12,
                                        pyb.Pin.board.PB11, pyb.Pin.board.PC12,
                                            pyb.Pin.board.PC4)

    # Create Feedback Tasks
    x_feedback = feedback_task_func.Feedback_Task(x_encoder, x_limit, x_zero,
                        1, pyb.Pin.board.PA8, pyb.Pin.board.PA9,
                            pyb.Pin.board.PB4,pyb.Pin.board.PC13, 'X ')
    z_feedback = feedback_task_func.Feedback_Task(z_encoder, z_limit, z_zero,
                        2, pyb.Pin.board.PA0, pyb.Pin.board.PA1,
                            pyb.Pin.board.PB5, pyb.Pin.board.PA11, 'Z ')
    y_feedback = feedback_task_func.Feedback_Task(y_encoder, y_limit, y_zero,
                        3, pyb.Pin.board.PA6, pyb.Pin.board.PA7,
                            pyb.Pin.board.PB3, pyb.Pin.board.PB2, 'Y ')
    p_feedback = feedback_task_func.Feedback_Task(p_encoder, p_limit, p_zero,
                        4, pyb.Pin.board.PB6, pyb.Pin.board.PB7,
                            pyb.Pin.board.PA4, pyb.Pin.board.PH0, 'P ')

    # Create Motor Tasks
    x_motor = motor_task_func.Motor_Task(x_params, x_steps, x_enable, x_status, x_limit,
                    pyb.Pin.board.PC8, pyb.Pin.board.PB1, pyb.Pin.board.PH1,
                        pyb.Pin.board.PC2, 8, 3, 5, 3, 'X ')
    z_motor = motor_task_func.Motor_Task(z_params, z_steps, z_enable, z_status, z_limit,
                    pyb.Pin.board.PC6, pyb.Pin.board.PC11, pyb.Pin.board.PA15,
                        pyb.Pin.board.PC3, 8, 1, 5, 1, 'Z ')
    y_motor = motor_task_func.Motor_Task(y_params, y_steps, y_enable, y_status, y_limit,
                    pyb.Pin.board.PC7, pyb.Pin.board.PC5, pyb.Pin.board.PD2,
                        pyb.Pin.board.PC1, 8, 2, 5, 2, 'Y ')
    p_motor = motor_task_func.Motor_Task(p_params, p_steps, p_enable, p_status, p_limit,
                    pyb.Pin.board.PC9, pyb.Pin.board.PA5, pyb.Pin.board.PB9,
                        pyb.Pin.board.PC0, 8, 4, 5, 4, 'P ')


    ####################################################################
    ############################## TASKS ###############################
    ####################################################################

    # Hub Task
    task1 = cotask.Task (hub.hub_fun, name = 'Task_1', priority = 1,
                            period = 50, profile = True, trace = False)

    # Feedback Tasks
    task2 = cotask.Task (x_feedback.fb_fun, name = 'Task_2', priority = 5,
                            period = 10, profile = True, trace = False)
    task3 = cotask.Task (z_feedback.fb_fun, name = 'Task_3', priority = 5,
                            period = 10, profile = True, trace = False)
    task4 = cotask.Task (y_feedback.fb_fun, name = 'Task_4', priority = 5,
                            period = 10, profile = True, trace = False)
    task5 = cotask.Task (p_feedback.fb_fun, name = 'Task_5', priority = 5,
                            period = 10, profile = True, trace = False)

    # Motor Tasks
    task6 = cotask.Task (x_motor.mot_fun, name = 'Task_6', priority = 3,
                            period = 20, profile = True, trace = False)
    task7 = cotask.Task (z_motor.mot_fun, name = 'Task_7', priority = 3,
                            period = 20, profile = True, trace = False)
    task8 = cotask.Task (y_motor.mot_fun, name = 'Task_8', priority = 3,
                            period = 20, profile = True, trace = False)
    task9 = cotask.Task (p_motor.mot_fun, name = 'Task_9', priority = 3,
                            period = 20, profile = True, trace = False)

    cotask.task_list.append (task1)
    cotask.task_list.append (task2)
    cotask.task_list.append (task3)
    cotask.task_list.append (task4)
    cotask.task_list.append (task5)
    cotask.task_list.append (task6)
    cotask.task_list.append (task7)
    cotask.task_list.append (task8)
    cotask.task_list.append (task9)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    ####################################################################
    ############################### RUN ################################
    ####################################################################

    print('Running the MUVI Manipulator RTOS')
    # Run the scheduler with the chosen scheduling algorithm
    while True:
        cotask.task_list.pri_sched()
