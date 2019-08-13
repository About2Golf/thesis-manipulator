

import pyb
import utime

vcp = pyb.USB_VCP ()
print('hi')

while(1):
    if vcp.any(): 
        y = int(vcp.read(2).decode('UTF-8'))
        print('The number is:' +str(y))