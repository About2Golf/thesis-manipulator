import pyb

## Set Pin PA10 toas open-drain output with pull up resistors
#EN_Pin=pyb.Pin(pyb.Pin.board.PA10,pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP)
## Set Pin PB4 as push-pull with the correct alternate function (timer)
Pin_1=pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP) 
## Set Pin PB5 as push-pull with the correct alternate function (timer)
Pin_2=pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_OD, pull=pyb.Pin.PULL_UP) 

#EN_Pin.low()                                         # Set Pins Low on startup 
Pin_1.low()
Pin_2.low()
print('We are On')

