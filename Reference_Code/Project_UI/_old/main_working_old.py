

import pyb
import utime

vcp = pyb.USB_VCP ()
print('hi')
y = 0

while(1):
    if vcp.any(): 
        vcp.read()
        y += 1
        print(y)