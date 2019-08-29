"""
Created on Fri Feb 16 16:53:17 2018

@privatesection - Stuff in this file doesn't need to be Doxygen-ed

@author: JasonGrillo
"""

import pyb
import micropython
import gc

import cotask
import task_share

import motor_task_func
import feedback_task_func
import hub_task_func
import gui_task_func

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

    # params: [status: zero or position; target: 60 steps; speed: 14 steps/sec; accel: 20 steps/sec^2]
    x_params = task_share.Queue ('b', 5, thread_protect = False,
                                   overwrite = False, name = "x_params")
    z_params = task_share.Queue ('b', 5, thread_protect = False,
                                   overwrite = False, name = "z_params")
    y_params = task_share.Queue ('b', 5, thread_protect = False,
                                   overwrite = False, name = "y_params")
    p_params = task_share.Queue ('b', 5, thread_protect = False,
                                   overwrite = False, name = "p_params")

    # HIGO = task_share.Queue ('b', 50, thread_protect = False,
    #                                overwrite = False, name = "HIGO")
    # HOGI = task_share.Queue ('b', 50, thread_protect = False,
    #                                overwrite = False, name = "HOGI")

    x_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "x_encoder")
    z_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "z_encoder")
    y_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "y_encoder")
    p_encoder = task_share.Share ('f', thread_protect = False,
                                     name = "p_encoder")

    x_limit = task_share.Share ('i', thread_protect = False,
                                     name = "x_limit")
    z_limit = task_share.Share ('i', thread_protect = False,
                                     name = "z_limit")
    y_limit = task_share.Share ('i', thread_protect = False,
                                     name = "y_limit")
    p_limit = task_share.Share ('i', thread_protect = False,
                                     name = "p_limit")

    x_enable = task_share.Share ('i', thread_protect = False,
                                     name = "x_enable")
    z_enable = task_share.Share ('i', thread_protect = False,
                                     name = "z_enable")
    y_enable = task_share.Share ('i', thread_protect = False,
                                     name = "y_enable")
    p_enable = task_share.Share ('i', thread_protect = False,
                                     name = "p_enable")

    x_zero = task_share.Share ('i', thread_protect = False,
                                     name = "x_zero")
    z_zero = task_share.Share ('i', thread_protect = False,
                                     name = "z_zero")
    y_zero = task_share.Share ('i', thread_protect = False,
                                     name = "y_zero")
    p_zero = task_share.Share ('i', thread_protect = False,
                                     name = "p_zero")

    ####################################################################
    ########################## TASK OBJECTS ############################
    ####################################################################

    # Create Hub Task
    hub = hub_task_func.Hub_Task(x_params, z_params, y_params, p_params,
                                    x_enable, z_enable, y_enable, p_enable,
                                    x_encoder, z_encoder, y_encoder, p_encoder,
                                    x_limit, z_limit, y_limit, p_limit,
                                    x_zero, z_zero, y_zero, p_zero)

    # # Create GUI Task
    # gui = gui_task_func.GUI_Task(HIGO, HOGI, x_encoder, z_encoder, y_encoder, p_encoder, x_limit, z_limit, y_limit, p_limit, x_enable, z_enable, y_enable, p_enable)

    # Create Feedback Tasks
    x_feedback = feedback_task_func.Feedback_Task(x_encoder, x_limit, x_zero,
                                                    4, pyb.Pin.board.PB6, pyb.Pin.board.PB7,
                                                    pyb.Pin.board.P,pyb.Pin.board.P)
    z_feedback = feedback_task_func.Feedback_Task(z_encoder, z_limit, z_zero,
                                                    4, pyb.Pin.board.PB6, pyb.Pin.board.PB7,
                                                    pyb.Pin.board.P,pyb.Pin.board.P)
    y_feedback = feedback_task_func.Feedback_Task(y_encoder, y_limit, y_zero,
                                                    4, pyb.Pin.board.PB6, pyb.Pin.board.PB7,
                                                    pyb.Pin.board.P,pyb.Pin.board.P)
    p_feedback = feedback_task_func.Feedback_Task(p_encoder, p_limit, p_zero,
                                                    4, pyb.Pin.board.PB6, pyb.Pin.board.PB7,
                                                    pyb.Pin.board.P,pyb.Pin.board.P)

    # Create Motor Tasks
    x_motor = motor_task_func.Motor_Task(x_params, x_enable,
                                           pyb.Pin.board.PA11,
                                           pyb.Pin.board.PB1,
                                           pyb.Pin.board.PC8,
                                           pyb.Pin.board.PC9,
                                           pyb.Pin.board.PC2,
                                           timer, channel)
    z_motor = motor_task_func.Motor_Task(z_params, z_enable,
                                           pyb.Pin.board.PB12,
                                           pyb.Pin.board.PB15,
                                           pyb.Pin.board.PC6,
                                           pyb.Pin.board.PB9,
                                           pyb.Pin.board.PC3,
                                           timer, channel)
    y_motor = motor_task_func.Motor_Task(y_params, y_enable,
                                           pyb.Pin.board.PB11,
                                           pyb.Pin.board.PB14,
                                           pyb.Pin.board.PC5,
                                           pyb.Pin.board.PA15,
                                           pyb.Pin.board.PC1,
                                           timer, channel)
    p_motor = motor_task_func.Motor_Task(p_params, p_enable,
                                           pyb.Pin.board.PB2,
                                           pyb.Pin.board.PB13,
                                           pyb.Pin.board.PA5,
                                           pyb.Pin.board.PH1,
                                           pyb.Pin.board.PC0,
                                           timer, channel)

    ####################################################################
    ############################## TASKS ###############################
    ####################################################################

    # Hub Task
    task1 = cotask.Task (hub.hub_fun, name = 'Task_1', priority = 1,
                         period = 100, profile = True, trace = False)

    # Feedback Tasks
    task2 = cotask.Task (x_feedback.fb_fun, name = 'Task_2', priority = 5,
                     period = 5, profile = True, trace = False)
    task3 = cotask.Task (z_feedback.fb_fun, name = 'Task_3', priority = 5,
                         period = 5, profile = True, trace = False)
    task4 = cotask.Task (y_feedback.fb_fun, name = 'Task_4', priority = 5,
                         period = 5, profile = True, trace = False)
    task5 = cotask.Task (p_feedback.fb_fun, name = 'Task_5', priority = 5,
                         period = 5, profile = True, trace = False)

    # Motor Tasks
    task6 = cotask.Task (x_motor.mot_fun, name = 'Task_6', priority = 3,
                         period = 20, profile = True, trace = False)
    task7 = cotask.Task (z_motor.mot_fun, name = 'Task_7', priority = 3,
                         period = 20, profile = True, trace = False)
    task8 = cotask.Task (y_motor.mot_fun, name = 'Task_8', priority = 3,
                         period = 20, profile = True, trace = False)
    task9 = cotask.Task (p_motor.mot_fun, name = 'Task_9', priority = 3,
                         period = 20, profile = True, trace = False)

    # # GUI Task
    # task10 = cotask.Task (gui.gui_fun, name = 'Task_10', priority = 2,
    #                      period = 50, profile = True, trace = False)

    cotask.task_list.append (task1)
    cotask.task_list.append (task2)
    cotask.task_list.append (task3)
    cotask.task_list.append (task4)
    cotask.task_list.append (task5)
    cotask.task_list.append (task6)
    cotask.task_list.append (task7)
    cotask.task_list.append (task8)
    cotask.task_list.append (task9)
    # cotask.task_list.append (task10)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    ####################################################################
    ############################### RUN ################################
    ####################################################################

    # Run the scheduler with the chosen scheduling algorithm
    while True:
        cotask.task_list.pri_sched()
