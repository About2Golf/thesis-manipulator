
## First order step response test

"""

@author: mecha10, JGrillo, TGoehring, TPeterson
"""

import pyb
import task_share

#Set up queue using task share, unsigned integers, queue size of 1000 with
#thread protection for interrupts
q0 = task_share.Queue ('I', 1000, thread_protect = True, overwrite = False,
                           name = "Queue_0")

#Set up PC1 as an output to the circuit
PinPC1=pyb.Pin(pyb.Pin.board.PC1,pyb.Pin.OUT_PP, pull=pyb.Pin.PULL_UP)
#Set up PC0 as an input to the ADC
PinPC0=pyb.Pin(pyb.Pin.board.PC0,pyb.Pin.IN)
#Timer 1 with a 1KHz frequency
Timer= pyb.Timer(1, freq=1000)
#Set up ADC reading from PinPC0
adcpin = pyb.ADC (PinPC0)
#Create tick function that receives the timer object when called
def tick(Timer):
    if not q0.full(): #if the queue is not full, load ADC
        volts = adcpin.read () #read ADC
        q0.put(volts,in_ISR=True) #Put volts into queue
    else:
        Timer.callback(None) #If full, turn off the interrupt

if __name__ == "__main__":
    print('Running the stupid code')
    PinPC1.high()
    Timer.callback(tick)
    while True:
        if q0.full():
            PinPC1.low()
            xdata = [i for i in range(1000)]
            ydata = []
            for i in range(1000):
                queue = q0.get(in_ISR=False)
                ydata.append(queue)
            for (time,voltage) in zip(xdata,ydata): # Referenced https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
                print(str(time) + ',' + str(voltage))
