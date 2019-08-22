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

    # #Pan Coordinates Queue is used to deliver target pan encoder value to
    # #Pan Motor Task from Turret Hub Task
    # pan_coords = task_share.Queue ('f', 2, thread_protect = False,
    #                                overwrite = False, name = "Pan_Coords")
    #
    # #Tilt Coordinates Queue is used to deliver target tilt IMU value to
    # #Tilt Motor Task from Turret Hub Task
    # tilt_coords = task_share.Queue ('f', 2, thread_protect = False,
    #                                 overwrite = False, name = "Tilt_Coords")
    #
    # #Pan Position Share is used to deliver current encoder value to
    # #to the Turret Hub and Pan Motor tasks from the Encoder Task
    # pan_position = task_share.Share ('f', thread_protect = False,
    #                                  name = "Pan_Position")
    #
    # #Tilt Angle Share is used to deliver current IMU pitch value to
    # #to the Turret Hub and Tilt Motor tasks from the Encoder Task
    # tilt_angle = task_share.Share ('f', thread_protect = False,
    #                                name = "Tilt_Position")
    #
    # #Share Sent from Turret Hub Task to Nerf Gun Task to Start Feeding Bullets
    # FEED_BULLETS = task_share.Share('f', thread_protect = False,
    #                                 name = "Feed_Bullets")
    #
    # #Share sent from Turret Hub Task to Nerf Gun Task to
    # WINDUP_GUN = task_share.Share ('f', thread_protect = False,
    #                                name = "Windup_Gun")

    ####################################################################
    ########################## TASK OBJECTS ############################
    ####################################################################

    # pan_encoder = encoder_task_func.Encoder_Task(pan_position, 4,
    #                                  pyb.Pin.board.PB6, pyb.Pin.board.PB7)

    # tilt_IMU = IMU_task_func.IMU_Task(tilt_angle) #what to put here 0 for tilt angle

    #0.02
    x_motor = motor_task_func.Motor_Task(pyb.Pin.board.PA11,
                                           pyb.Pin.board.PB1,
                                           pyb.Pin.board.PC8,
                                           pyb.Pin.board.PC9,
                                           pyb.Pin.board.PC2)
    z_motor = motor_task_func.Motor_Task(pyb.Pin.board.PB12,
                                           pyb.Pin.board.PB15,
                                           pyb.Pin.board.PC6,
                                           pyb.Pin.board.PB9,
                                           pyb.Pin.board.PC3)
    yaw_motor = motor_task_func.Motor_Task(pyb.Pin.board.PB11,
                                           pyb.Pin.board.PB14,
                                           pyb.Pin.board.PC5,
                                           pyb.Pin.board.PA15,
                                           pyb.Pin.board.PC1)
    pan_motor = motor_task_func.Motor_Task(pyb.Pin.board.PB2,
                                           pyb.Pin.board.PB13,
                                           pyb.Pin.board.PA5,
                                           pyb.Pin.board.PH1,
                                           pyb.Pin.board.PC0)
    # turret_hub = turret_hub_task_func.Turret_Hub_Task(pan_position, tilt_angle, pan_coords,
    #                                                   tilt_coords, FEED_BULLETS, WINDUP_GUN)
    #
    # nerf_gun = nerf_task_func.Nerf_Task(WINDUP_GUN, FEED_BULLETS, pyb.Pin.board.PC7, pyb.Pin.board.PC6)

    ####################################################################
    ############################## TASKS ###############################
    ####################################################################
    #
    # #Turret Hub Timing => Timing: 100 ms, Priority 1 (Lowest)
    # task0 = cotask.Task (turret_hub.turret_hub_fun, name = 'Task_0', priority = 1,
    #                      period = 100, profile = True, trace = False)
    # #Pan Encoder => Timing 2 ms, Priority 5(Highest)
    # task1 = cotask.Task (pan_encoder.enc_fun, name = 'Task_1', priority = 5,
    #                      period = 2, profile = True, trace = False)
    # #Tilt IMU => Timing 5 ms (minimum 10 ms, applied 2x SF), Priority 5(Highest)
    # # task2 = cotask.Task (tilt_IMU.IMU_fun, name = 'Task_2', priority = 5,
    # #                      period = 5, profile = True, trace = False)
    #X Motor => Timing 20 ms, Priority 3 (Medium)
    task6 = cotask.Task (x_motor.mot_fun, name = 'Task_6', priority = 3,
                         period = 20, profile = True, trace = False)
    #Z Motor => Timing 20 ms, Priority 3 (Medium)
    task7 = cotask.Task (z_motor.mot_fun, name = 'Task_7', priority = 3,
                         period = 50, profile = True, trace = False)
    #Yaw Motor => Timing 20 ms, Priority 3 (Medium)
    task8 = cotask.Task (yaw_motor.mot_fun, name = 'Task_8', priority = 3,
                         period = 20, profile = True, trace = False)
    #Pan Motor => Timing 20 ms, Priority 3 (Medium)
    task9 = cotask.Task (pan_motor.mot_fun, name = 'Task_9', priority = 3,
                         period = 50, profile = True, trace = False)
    # #Nerf Gun => Timing 200 ms, Priority 1 (Lowest)
    # task5 = cotask.Task (nerf_gun.gun_fun, name = 'Task_5', priority = 1,
    #                      period = 200, profile = True, trace = False)

    # cotask.task_list.append (task0)
    # cotask.task_list.append (task1)
    # # cotask.task_list.append (task2)
    # cotask.task_list.append (task3)
    # cotask.task_list.append (task4)
    # cotask.task_list.append (task5)
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

    # Run the scheduler with the chosen scheduling algorithm
    while True:
        cotask.task_list.pri_sched()
