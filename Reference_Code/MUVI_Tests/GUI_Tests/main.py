import pyb
import micropython
import gc



# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
micropython.alloc_emergency_exception_buf (100)


# =========================================================================== #
# ======================== Run the Turret Code ============================== #
# =========================================================================== #

if __name__ == "__main__":
    vcp = pyb.USB_VCP()
    print('vcp setup')

    while (True):
        # print(vcp.isconnected())
        # GUI_input = float(b'm;p;1000;1;50;6000;50'.decode('UTF-8'))
        # print(GUI_input)
        if vcp.any():
            print('command received')
            GUI_input = vcp.read().decode('UTF-8')
            # print(GUI_input)
