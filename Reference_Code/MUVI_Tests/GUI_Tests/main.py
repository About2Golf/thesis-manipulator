import pyb
import micropython
import gc
import utime


# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
micropython.alloc_emergency_exception_buf (100)


# =========================================================================== #
# ======================== Run the Turret Code ============================== #
# =========================================================================== #

if __name__ == "__main__":
    # vcp = pyb.USB_VCP()
    # print('running')
    uart = pyb.UART(2,115200)
    uart.init(115200, bits=8, parity=None, stop=1)
    #
    # print(c'ready to run')
    print ('r'.encode('UTF-8'), end = '')
    # while (True):
        # uart.write('1\r\n')
        # utime.sleep_ms(10)
        # if uart.any():
        #     input = uart.read().decode('UTF-8')
        #     print(input)
    #     # print(vcp.isconnected())
    #     # GUI_input = float(b'm;p;1000;1;50;6000;50'.decode('UTF-8'))
    #     # print(GUI_input)
    #     if vcp.any():
    #         print('command received')
    #         GUI_input = vcp.read().decode('UTF-8')
    #         print(GUI_input)
