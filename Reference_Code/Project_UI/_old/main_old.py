

import pyb
import utime

vcp = pyb.USB_VCP ()
print('hi')

while(1):
    if vcp.any(): 
        y = vcp.read(2)
        print('The number is:' +str(y))