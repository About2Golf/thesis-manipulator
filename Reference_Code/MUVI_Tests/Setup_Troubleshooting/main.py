
## First order step response test

"""

@author: mecha10, JGrillo, TGoehring, TPeterson
"""

import pyb
import micropython
import machine
import task_share
import output_pin
import utime
import steppin

micropython.alloc_emergency_exception_buf(100)
#
# #Set up queue using task share, unsigned integers, queue size of 1000 with
# #thread protection for interrupts
# q0 = task_share.Queue ('I', 1000, thread_protect = True, overwrite = False,
#                            name = "Queue_0")
#
# #Set up PC1 as an output to the circuit
# PinPC1=machine.Pin(pyb.Pin.board.PC9, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
# #Set up PC0 as an input to the ADC
# PinPC0=machine.Pin(pyb.Pin.board.PC0, machine.Pin.IN, machine.Pin.PULL_UP)
# #Timer 1 with a 1KHz frequency
# Timer= pyb.Timer(4, freq=1)
# #Set up ADC reading from PinPC0
# adcpin = pyb.ADC (PinPC0)
# #Create tick function that receives the timer object when called
# def tick(Timer):
#     if not PinPC1.value():
#         PinPC1.high()
#     else:
#         PinPC1.low()
#     # print('inside tick')
#     # if not q0.full(): #if the queue is not full, load ADC
#     #     volts = adcpin.read () #read ADC
#     #     q0.put(volts,in_ISR=True) #Put volts into queue
#     # else:
#     #     Timer.callback(None) #If full, turn off the interrupt

if __name__ == "__main__":
    # import machine

    # def tick(timer):                # we will receive the timer object when being called
    #     # print(timer.counter())      # show current timer's counter value
    #     if not PinPC1.value():
    #         PinPC1.high()
    #     else:
    #         PinPC1.low()
    # tim = pyb.Timer(8, freq=1)      # create a timer object using timer 4 - trigger at 1Hz
    # tim.callback(tick)              # set the callback to our tick function


        # self.pin=pyb.Pin(pin, pyb.Pin.AF_PP,af=alt_fun)
        # ## Set Pin PB5 as push-pull with the correct alternate function (timer)
        # # self.Pin_2=pyb.Pin(Pin_2, pyb.Pin.AF_PP,af=2)
        # self.timer= pyb.Timer(timer, freq = 2)                             # Set Timer 3 to a frequency of 20,000 Hz
        # self.channel = self.timer.channel(channel, pyb.Timer.PWM, pin=self.pin) # Set Timer 3 Channel 1 to PWM for pin PB4
    #
    # class StepPin(object):
    #     def __init__(self, step_timer, step_channel, pin, init_speed, accel_timer, accel_ch, accel_rate, name):
    #         # self.pin=pyb.Pin(pin, pyb.Pin.AF_PP,af=3)
    #         # self.led = machine.Pin(led, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
    #         self.pin = machine.Pin(pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
    #         self.init_speed = init_speed
    #         self.step_rate = self.init_speed
    #         self.step_timer = pyb.Timer(step_timer, freq=self.step_rate)
    #         # self.channel = self.timer.channel(channel, pyb.Timer.PWM, pin=self.pin)
    #         self.step_channel = self.step_timer.channel(step_channel, pyb.Timer.OC_TIMING, callback=self.cb)
    #         self.accel_rate = accel_rate
    #         self.accel_timer = pyb.Timer(accel_timer, freq=self.accel_rate)
    #         # self.channel = self.timer.channel(channel, pyb.Timer.PWM, pin=self.pin)
    #         self.accel_channel = self.accel_timer.channel(accel_channel, pyb.Timer.OC_TIMING, callback=self.accel_cb)
    #         self.stepping = 0
    #         self.accelerating = 0
    #         self.step_count = 0
    #         self.total_steps = 0
    #         self.ramp_step_number = 0
    #         self.name = name
    #         # self.channel.callback(self.cb)
    #
    #     def start_stepping(self, counts):
    #         self.stepping = 1
    #         self.accelerating = 1
    #         self.total_steps = counts
    #         self.accel_steps = round(self.total_steps*0.20)
    #         # self.channel.callback(self.cb)
    #
    #     def stop_stepping(self):
    #         self.stepping = 0
    #         self.accelerating = 0
    #         self.step_count = 0
    #         self.total_steps = 0
    #         self.step_rate = self.init_speed
    #         # self.channel.callback(None)
    #
    #     def set_step_freq(self,step_rate):
    #         self.step_timer.freq(step_rate)
    #
    #     def set_accel_rate(self,accel_rate):
    #         self.accel_timer.freq(accel_rate)
    #
    #     def cb(self, tim):
    #         if self.stepping:
    #             self.step_count +=1
    #             if self.step_count < total_steps:
    #                 if not self.pin.value():
    #                     self.pin.value(1)
    #                 else:
    #                     self.pin.value(0)
    #             else:
    #                 self.accelerating = 0
    #                 self.step_count = 0
    #                 self.total_steps = 0
    #                 self.step_rate = self.init_speed
    #         else:
    #             self.pin.value(0)
    #
    #     def accel_cb(self, tim):
    #         if self.accelerating:
    #             if self.step_count < self.accel_steps:
    #                 self.step_rate += 1
    #                 self.step_timer.freq(self.step_rate)
    #             else:
    #                 self.accelerating = 0
    #         else:
    #             # print('not stepping')

    x_step = steppin.StepPin(8, 3, pyb.Pin.board.PC8, pyb.Pin.board.PC2, 1, 30, 5, 5, 3, 'x')
    z_step = steppin.StepPin(8, 1, pyb.Pin.board.PC6, pyb.Pin.board.PC3, 1, 30, 5, 5, 1, 'z')
    y_step = steppin.StepPin(8, 2, pyb.Pin.board.PC7, pyb.Pin.board.PC1, 1, 30, 5, 5, 2, 'y')
    p_step = steppin.StepPin(8, 4, pyb.Pin.board.PC9, pyb.Pin.board.PC0, 1, 30, 5, 5, 4, 'p')
    # p_step = StepPin(8, 4, pyb.Pin.board.PC9, 'p')




#     enn_csn_x = output_pin.Output_Pin(pyb.Pin.board.PC10, 'enn_csn_x')
#     enn_csn_z = output_pin.Output_Pin(pyb.Pin.board.PB12, 'enn_csn_z')
#     enn_csn_y = output_pin.Output_Pin(pyb.Pin.board.PB11, 'enn_csn_y')
#     enn_csn_p = output_pin.Output_Pin(pyb.Pin.board.PC12, 'enn_csn_p')
# #
#     dir_x = output_pin.Output_Pin(pyb.Pin.board.PB1, 'dir_x')
#     dir_z = output_pin.Output_Pin(pyb.Pin.board.PC11, 'dir_z')
#     dir_y = output_pin.Output_Pin(pyb.Pin.board.PC5, 'dir_y')
#     dir_p = output_pin.Output_Pin(pyb.Pin.board.PA5, 'dir_p')
#
#     drv_enn_x = output_pin.Output_Pin(pyb.Pin.board.PH1, 'drv_enn_x')
#     drv_enn_z = output_pin.Output_Pin(pyb.Pin.board.PA15, 'drv_enn_z')
#     drv_enn_y = output_pin.Output_Pin(pyb.Pin.board.PD2, 'drv_enn_y')
#     drv_enn_p = output_pin.Output_Pin(pyb.Pin.board.PB9, 'drv_enn_p')
#
#     drv_enn_x.set_low()
#     drv_enn_z.set_low()
#     drv_enn_y.set_low()
#     drv_enn_p.set_low()
#
#     enn_csn_x.set_high()
#     enn_csn_z.set_high()
#     enn_csn_y.set_high()
#     enn_csn_p.set_high()
#
#     dir_x.set_high()
#     dir_z.set_high()
#     dir_y.set_high()
#     dir_p.set_high()
#
#     spi2 = pyb.SPI(2,pyb.SPI.MASTER, prescaler=64, polarity=1, phase=1, crc=0x7)
#     # spi2 = pyb.SPI(2,pyb.SPI.MASTER, baudrate=600000, polarity=1, phase=0, crc=0x7)
#
#     def convert_hexstring_to_bytearray(hex):
#         decimal_str = str(hex)
#         return decimal_str.encode('ascii')
#
#     def convert_bytearray_to_hexstring(byte_array):
#         data_decode = ustruct.unpack('<h',byte_array)
#         return
#
#     def send_recv_spi_data(data, enable_pin):
#         # enable_pin.set_low()
#         # spi2.send_recv(data)
#         # enable_pin.set_high()
#         enable_pin.set_low()
#         return_data = spi2.send_recv(data)
#         enable_pin.set_high()
#         return return_data
#
#     def send_spi_data(data, enable_pin):
#         # enable_pin.set_low()
#         # spi2.send(data)
#         # enable_pin.set_high()
#         enable_pin.set_low()
#         spi2.send(data)
#         enable_pin.set_high()
#
#     spi_command0 = b'\x00\x00\x00\x00\x00'
#     CHOPCONF = b'\xEC\x00\x01\x00\x43'
#     IHOLD_IRUN = b'\x90\x00\x06\x1F\x0A'
#     TPOWERDOWN = b'\x91\x00\x00\x00\x0A'
#     EN_PWM_MODE = b'\x80\x00\x00\x00\x04'
#     TPWM_THRS = b'\x93\x00\x00\x01\xF4'
#     PIN_STATUS = b'\x04\x00\x00\x00\x00'
#
#     print('Ready to Send Commands')
#     # send_recv_spi_data(spi_command1,enn_csn_p)
#     # # send_recv_spi_data(spi_command1,enn_csn_p)
#     # send_recv_spi_data(spi_command2,enn_csn_p)
#     # # send_recv_spi_data(spi_command2,enn_csn_p)
#     # send_recv_spi_data(spi_command3,enn_csn_p)
#     # # send_recv_spi_data(spi_command3,enn_csn_p)
#     # send_recv_spi_data(spi_command4,enn_csn_p)
#     # # send_recv_spi_data(spi_command4,enn_csn_p)
#     # send_recv_spi_data(spi_command5,enn_csn_p)
#     # # send_recv_spi_data(spi_command5,enn_csn_p)
#
#     send_spi_data(CHOPCONF,enn_csn_p)
#     utime.sleep_ms(2)
#     send_spi_data(IHOLD_IRUN,enn_csn_p)
#     utime.sleep_ms(2)
#     send_spi_data(TPOWERDOWN,enn_csn_p)
#     utime.sleep_ms(2)
#     send_spi_data(EN_PWM_MODE,enn_csn_p)
#     utime.sleep_ms(2)
#     send_spi_data(TPWM_THRS,enn_csn_p)
#     # utime.sleep_ms(5)
#     # send_spi_data(PIN_STATUS,enn_csn_p)
#
#     #
#     # print('sending spi command')
#     # spi_command = str(0x5555555555)
#     # enn_csn_p.set_low()
#     # spi2.send(spi_command)
#     # enn_csn_p.set_high()









    # interruptCounter = 0
    # totalInterruptsCounter = 0
    #
    # timer = pyb.Timer(4, freq=1)
    #
    # def handleInterrupt(timer):
    #   global interruptCounter
    #   interruptCounter = interruptCounter+1
    #
    # timer.callback(handleInterrupt)
    # # timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handleInterrupt)
    #
    # while True:
    #   if interruptCounter>0:
    #     state = machine.disable_irq()
    #     interruptCounter = interruptCounter-1
    #     machine.enable_irq(state)
    #
    #     totalInterruptsCounter = totalInterruptsCounter+1
    #     print("Interrupt has occurred: " + str(totalInterruptsCounter))

    # tim4 = pyb.Timer(4, freq=1)
    # tim7 = pyb.Timer(7, freq=20)
    # while True:
    # tim4.callback(lambda t: pyb.LED(1).toggle())
    # tim7.callback(lambda t: pyb.LED(2).toggle())
    # print('Running the stupid code')
    # # PinPC1.high()
    # Timer.callback(tick)
    #
    # # while True:
    #     # print('running')
    # #     if q0.full():
    # #         PinPC1.low()
    # #         xdata = [i for i in range(1000)]
    # #         ydata = []
    # #         for i in range(1000):
    # #             queue = q0.get(in_ISR=False)
    # #             ydata.append(queue)
    # #         for (time,voltage) in zip(xdata,ydata): # Referenced https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
    # #             print(str(time) + ',' + str(voltage))
