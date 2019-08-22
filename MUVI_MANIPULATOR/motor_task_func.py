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

    def __init__(self, EN_Pin, step_pin, dir_pin, Diag0_pin, Diag1_pin):
        ''' Construct a motor task function by initilizing any shared
            variables and initialize the motor object
            @param EN_pin The Motor's CSN and Enable pin (shared)
            @param step_pin The motor's step pin
            @param dir_pin The motor's direction pin
            @param Diag0_pin The motor's diagnostic pin 0
            @param Diag1_pin The motor's diagnostic pin 1
        '''
        # self.position = position
        # self.coordinate = coordinate
        self.Motor = motor.MotorDriver(EN_Pin, step_pin, dir_pin, Diag0_pin, Diag1_pin)
        # self.Controller = controller.Controller(Kp, Ki, Kd, saturation)

    def mot_fun(self):
        ''' Defines the task function method for a Motor object.
        '''
        STATE_0 = micropython.const (0)
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)
        STATE_3 = micropython.const (3)

        self.state = STATE_0
        self.counter = 0

        while True:
            ## STATE 0: Idle
            self.counter+=1

            if self.state == STATE_0:
                # Stop motor
                self.Motor.generate_pulse(0)
                self.Motor.disable_motor()
                if (self.counter >30):
                    self.counter = 0
                    self.state = STATE_1

            ## STATE 1: Accelerating
            elif self.state == STATE_1:
                # if self.coordinate.any():
                #     print('new coordinate to move to!')
                #     self.Controller.clear_controller()
                #     self.Controller.set_setpoint(self.coordinate.get())
                # Use controller object to get appropriate duty cycle for motor
                # self.Duty_Cycle = self.Controller.repeatedly(self.position.get())
                # Set duty cycle to motor
                # self.Motor.set_duty_cycle(self.Duty_Cycle)
                if (self.counter > 15):
                    self.Motor.set_direction(1)
                else:
                    self.Motor.set_direction(-1)
                self.Motor.generate_pulse(1)
                self.Motor.enable_motor()
                if (self.counter > 30):
                    self.counter = 0
                    self.state = STATE_2

            ## STATE 2: Max Velocity
            elif self.state == STATE_2:
                if (self.counter > 15):
                    self.Motor.set_direction(1)
                else:
                    self.Motor.set_direction(-1)
                self.Motor.generate_pulse(0)
                if (self.counter > 30):
                    self.counter = 0
                    self.state = STATE_1

            # ## STATE 3: Decelerating
            # elif self.state == STATE_3:
            #     self.Motor.generate_pulse(0)
            #     if (self.counter >30 and <60)
            #         self.state = STATE_1

            yield(self.state)
