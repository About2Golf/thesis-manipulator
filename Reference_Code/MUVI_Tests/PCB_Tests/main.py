"""
Created on Fri Feb 16 16:53:17 2018

@privatesection - Stuff in this file doesn't need to be Doxygen-ed

@author: JasonGrillo
"""

import pyb
import micropython
import ustruct

# import limit_switch
import encoder
import motor
import input_pin
import output_pin

# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
micropython.alloc_emergency_exception_buf (100)


if __name__ == "__main__":
#
    # diag0_x = input_pin.Input_Pin(pyb.Pin.board.PA12, 'diag0_x')
    # diag0_z = input_pin.Input_Pin(pyb.Pin.board.PB9, 'diag0_z')
    # diag0_y = input_pin.Input_Pin(pyb.Pin.board.PA15, 'diag0_y')
    # diag0_p = input_pin.Input_Pin(pyb.Pin.board.PH1, 'diag0_p')
#
    dco_x = input_pin.Input_Pin(pyb.Pin.board.PC2, 'dco_x')
    dco_z = input_pin.Input_Pin(pyb.Pin.board.PC3, 'dco_z')
    dco_y = input_pin.Input_Pin(pyb.Pin.board.PC1, 'dco_y')
    dco_p = input_pin.Input_Pin(pyb.Pin.board.PC0, 'dco_p')
#
    pLim_x = input_pin.Input_Pin(pyb.Pin.board.PC13, 'pLim_x')
    pLim_z = input_pin.Input_Pin(pyb.Pin.board.PA11, 'pLim_z')
    pLim_y = input_pin.Input_Pin(pyb.Pin.board.PB2, 'pLim_y')
    pLim_p = input_pin.Input_Pin(pyb.Pin.board.PH0, 'pLim_p')
#
    mLim_x = input_pin.Input_Pin(pyb.Pin.board.PB4, 'mLim_x')
    mLim_z = input_pin.Input_Pin(pyb.Pin.board.PB5, 'mLim_z')
    mLim_y = input_pin.Input_Pin(pyb.Pin.board.PB3, 'mLim_y')
    mLim_p = input_pin.Input_Pin(pyb.Pin.board.PA4, 'mLim_p')
#
    dir_x = output_pin.Output_Pin(pyb.Pin.board.PB1, 'dir_x')
    dir_z = output_pin.Output_Pin(pyb.Pin.board.PC11, 'dir_z')
    dir_y = output_pin.Output_Pin(pyb.Pin.board.PC5, 'dir_y')
    dir_p = output_pin.Output_Pin(pyb.Pin.board.PA5, 'dir_p')
#
    enn_csn_x = output_pin.Output_Pin(pyb.Pin.board.PC10, 'enn_csn_x')
    enn_csn_z = output_pin.Output_Pin(pyb.Pin.board.PB12, 'enn_csn_z')
    enn_csn_y = output_pin.Output_Pin(pyb.Pin.board.PB11, 'enn_csn_y')
    enn_csn_p = output_pin.Output_Pin(pyb.Pin.board.PC12, 'enn_csn_p')
#
    enn_csn_x.set_high()
    enn_csn_z.set_high()
    enn_csn_y.set_high()
    enn_csn_p.set_high()

    dcen = output_pin.Output_Pin(pyb.Pin.board.PC4, 'dcen')
#
    en_x = encoder.Encoder(1, pyb.Pin.board.PA8, pyb.Pin.board.PA9, 'en_x')
    en_z = encoder.Encoder(2, pyb.Pin.board.PA0, pyb.Pin.board.PA1, 'en_z')
    en_y = encoder.Encoder(3, pyb.Pin.board.PA6, pyb.Pin.board.PA7, 'en_y')
    en_p = encoder.Encoder(4, pyb.Pin.board.PB6, pyb.Pin.board.PB7, 'en_p')
#
    step_x = motor.MotorDriver(pyb.Pin.board.PC8, 8, 3, 3, 'step_x')
    step_z = motor.MotorDriver(pyb.Pin.board.PC6, 8, 1, 3, 'step_z')
    step_y = motor.MotorDriver(pyb.Pin.board.PC7, 8, 2, 3, 'step_y')
    step_p = motor.MotorDriver(pyb.Pin.board.PC9, 8, 4, 3, 'step_p')

    spi2 = pyb.SPI(2,pyb.SPI.MASTER, prescaler=256, crc=0x7)

    spi_command1 = b'\xEC\x00\x01\x00\xC3'
    spi_command2 = b'\x90\x00\x06\x1F\x0A'
    spi_command3 = b'\x91\x00\x00\x00\x0A'
    spi_command4 = b'\x80\x00\x00\x00\x04'
    spi_command5 = b'\x93\x00\x00\x01\xF4'

    print('Ready to Send Commands')
    # send_spi_data(spi_command1, enn_csn_p)
    # spi_command = str(0xEC000100C3)


    # enn_csn_p.set_low()
    # spi2.send(spi_command)
    # enn_csn_p.set_high()

def convert_hexstring_to_bytearray(hex):
    decimal_str = str(hex)
    return decimal_str.encode('ascii')

def convert_bytearray_to_hexstring(byte_array):
    data_decode = ustruct.unpack('<h',byte_array)
    return

def send_recv_spi_data(data, enable_pin):
    enable_pin.set_low()
    return_data = spi2.send_recv(data)
    enable_pin.set_high()
    return return_data

def send_spi_data(data, enable_pin):
    enable_pin.set_low()
    spi2.send(data)
    enable_pin.set_high()






    # pin = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.AF_PP, af=3)
    # timer = pyb.Timer(8, freq=5)
    # channel = timer.channel(1, pyb.Timer.PWM, pin=pin)
    # channel.pulse_width_percent(50)

    # pin = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.AF_PP, af=3)
    # timer = pyb.Timer(8, freq=5)
    # channel = timer.channel(2, pyb.Timer.PWM, pin=pin)
    # channel.pulse_width_percent(50)

    # pin = pyb.Pin(pyb.Pin.board.PC8, pyb.Pin.AF_PP, af=3)
    # timer = pyb.Timer(8, freq=5)
    # channel = timer.channel(3, pyb.Timer.PWM, pin=pin)
    # channel.pulse_width_percent(50)
    #
    # pin = pyb.Pin(pyb.Pin.board.PC9, pyb.Pin.AF_PP, af=3)
    # timer = pyb.Timer(8, freq=5)
    # channel = timer.channel(4, pyb.Timer.PWM, pin=pin)
    # channel.pulse_width_percent(50)

###
    # pin2 = pyb.Pin(pyb.Pin.board.PC8, pyb.Pin.AF_PP, af=2)
    # channel2 = timer_trans.channel(3, pyb.Timer.PWM, pin=pin2)
    # channel2.pulse_width_percent(50)
    #
    # pin3 = pyb.Pin('A2').init(pyb.Pin.AF_PP, af=2)
    # timer_rot= pyb.Timer(5, freq=2)
    # channel3 = timer_rot.channel(3, pyb.Timer.PWM, pin=pin3)
    # channel3.pulse_width_percent(50)
    #
    # pin4 = pyb.Pin('A3').init(pyb.Pin.AF_PP, af=2)
    # channel = timer.channel(4, pyb.Timer.PWM, pin=pin4)
    # channel.pulse_width_percent(50)
