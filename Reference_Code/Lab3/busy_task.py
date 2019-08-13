# -*- coding: utf-8 -*-
"""
@file busy_task.py
This file contains a task for testing the ME405 task scheduler. The task
doesn't do anything useful except to take up a lot of time, but since the 
scheduler is all about time, it makes a nice test. 

@author jr
@date Fri Jan  6 10:59:12 2017
@copyright GPL Version 3.0
"""

import print_task


class BusyTask:
    """ Class which contains a task function. This tests the use of a class
    method as a task function, and it allows lots of tasks to be easily made.
    """

    ## A serial number for @c BusyTask objects. This gives each created busy
    #  task a separate identifier. This is an example of a variable which
    #  "belongs to the class" rather than to any one instance of the class; 
    #  note that it's accessed as @c BusyTask.t_num, not @c self.t_num
    t_num = 0

    def __init__ (self):
        """ Initialize a busy task by creating its serial number. """

        ## The serial number of the busy task
        self.ser_num = BusyTask.t_num
        BusyTask.t_num += 1


    def run_fun (self):
        """ Run function for the @c BusyTask.  This function doesn't do much
        except to verify that a class member can be a task function. """

        while True:
            print_task.put ('[' + str (self.ser_num) + ']')
            yield (0)


