"""
Created on Fri Feb  9 23:53:47 2018

@author: JasonGrillo
"""
import encoder
import limit_switch
import micropython

class Feedback_Task:
    ''' This defines the task function method for an encoder and limit switch. The class
        passes its data via a shared variable with another task.
        To create an instance of this task class (example):
            # create encoder position shared variable
            pan_position = task_share.Share ('i', thread_protect = False,
                                               name = "Share_0_pan_position")
            # create encoder 1 task object
            pan_encoder = Encoder_Task(pan_position, 4,
                                     pyb.Pin.board.PB6, pyb.Pin.board.PB7)
            # create task1 function
            task1 = cotask.Task (pan_encoder.enc_fun(), name = 'Task_1', priority = 5,
                         period = 2, profile = True, trace = False)
            # append task1 to list of scheduled tasks
            cotask.task_list.append (task1)
    '''

    def __init__(self, encoder_share, limit_share, timer, enc_A, enc_B, ls_pin_m, ls_pin_p):
        ''' Construct an encoder task function by initilizing any shared
            variables and initialize the encoder object
            @param encoder_share The shared variable between tasks that contains the Encoder readings
            @param timer The Encoder's timer channel
            @param pin1 The Encoder's first pin, Pin A
            @param pin2 The Encoder's second pin, Pin B
        '''
        self.encoder = encoder_share
        self.limit = limit_share
        self.Encoder = encoder.Encoder(timer, enc_A, enc_B)
        self.Limit = limit_switch.Limit_Switch(ls_pin_m, ls_pin_p)

    def fb_fun(self):
        '''
        Defines the task function method for a Motor object.
        '''
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)

        self.state = STATE_1

        while True:
            ## STATE 1: Send Feedback
            if self.state == STATE_1:
                self.limit.put(self.Limit_Switch.read_limit())
                self.encoder.put(self.Encoder.read_encoder())
                if ():
                    self.state = STATE_2

            ## STATE 2: Zero Encoder
            elif self.state == STATE_2:
                self.Encoder.zero_encoder()



            yield(self.state)
