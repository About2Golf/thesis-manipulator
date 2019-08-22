"""
Created on Fri Feb 16 16:53:17 2018

@privatesection - Stuff in this file doesn't need to be Doxygen-ed

@author: JasonGrillo
"""

import pyb
import micropython


# =========================================================================== #
# ======================== Run the Turret Code ============================== #
# =========================================================================== #

if __name__ == "__main__":
    step_x = pyb.Pin(pyb.Pin.board.PB1,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
    step_z = pyb.Pin(pyb.Pin.board.PB15,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
    step_y = pyb.Pin(pyb.Pin.board.PB14,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
    step_p = pyb.Pin(pyb.Pin.board.PB13,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
    print('step_LEDs')
    step_x.high()
    step_z.high()
    step_y.high()
    step_p.high()
    pyb.delay(1500)
    step_x.low()
    step_z.low()
    step_y.low()
    step_p.low()
    #
    # # Run the scheduler with the chosen scheduling algorithm
    # while True:
    #     # pyb.LED(1).on()
    #     step_x.high()
    #     step_z.high()
    #     step_y.high()
    #     step_p.high()
    #     pyb.delay(1500)
    #     step_x.low()
    #     step_z.low()
    #     step_y.low()
    #     step_p.low()
    #     # pyb.LED(1).off()
