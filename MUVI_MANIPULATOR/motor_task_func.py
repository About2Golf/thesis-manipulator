"""
Created on Fri Feb  9 23:53:47 2018

@author: JasonGrillo
"""
import motor
import controller
import micropython

class Motor_Task:
    ''' This defines the task function method for a motor. The motor
        utilizes shared data from an encoder to know where it is.
        To create an instance of this task class (example):
            # have run shared variable declared
            Run = task_share.Share('i', thread_protect = False,
                                   name = "Run_Intertask_Comm_Variable")
            # have encoder position shared variable declared
            enc_1_position = task_share.Share ('i', thread_protect = False,
                                               name = "Share_0_enc_1_position")
            # create motor 1 task object
            Motor_1 = motor_task_func.Motor_Task(Run, enc_1_position, 4,
                                     pyb.Pin.board.PB6, pyb.Pin.board.PB7)
            # create task2 function, adjust parameters for implementation
            task2 = cotask.Task (Motor_1.enc_fun(), name = 'Task_2', priority = 5,
                         period = 2, profile = True, trace = False)
            # append task2 to list of scheduled tasks
            cotask.task_list.append (task2)
    '''

    def __init__(self, params, enable, EN_Pin, step_pin, dir_pin, Diag0_pin, Diag1_pin, timer, channel):
        ''' Construct a motor task function by initilizing any shared
            variables and initialize the motor object
            @param coordinate The motor's queue variable with the step info
            @param EN_pin The Motor's CSN and Enable pin (shared)
            @param step_pin The motor's step pin
            @param dir_pin The motor's direction pin
            @param Diag0_pin The motor's diagnostic pin 0
            @param Diag1_pin The motor's diagnostic pin 1
        '''
        self.params = params
        self.enable = enable
        self.Motor = motor.MotorDriver(EN_Pin, step_pin, dir_pin, Diag0_pin, Diag1_pin, timer, channel)

    def mot_fun(self):
        '''
        Defines the task function method for a Motor object.
        '''
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)
        STATE_3 = micropython.const (3)
        STATE_4 = micropython.const (4)

        self.state = STATE_1

        while True:
            ## STATE 1: Idle
            if self.state == STATE_1:
                check_disable()
                if self.params.any():
                    get_params()
                    self.Motor.set_setpoint(steps)
                    self.Motor.set_ramp_parameters(max_speed, accel_rate)
                    # generate ramp (steps, speed, acceleration)
                    self.state = STATE_2

            ## STATE 2: Accelerating
            elif self.state == STATE_2:
                check_disable()
                self.Motor.accelerate(accel_steps)
                # count steps...

            ## STATE 3: CONSTANT SPEED
            elif self.state == STATE_3:
                check_disable()
                # run the motor constant speed method

            ## STATE 4: Decelerating
            elif self.state == STATE_4:
                check_disable()
                # run the motor deceleration method

            yield(self.state)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def check_disable(self):
        '''
        '''
        if not self.enable.get():
            self.Motor.disable_motor()
        else:
            self.Motor.enable_motor()

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def get_params(self):
        '''
        '''
