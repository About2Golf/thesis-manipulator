# -*- coding: utf-8 -*-
"""
JYHoriba_mono.py 
The python wrapper for the monochromator so that it is compatible for higher-level integration
based on Kodi Rider's code
---
see link for documentation (below)
https://wanglib.readthedocs.io/en/latest/instruments/spex750m.html
---

written by Yuzo Ishikawa
"""
import sys
sys.path.insert(0, r"C:\Python27\Lib\site-packages\xy\wanglib-master")
import wanglib.instruments as instr

# make some default settings for now until the main GUI is ready
from time import sleep
global com_port 
#com_port = 9


# ====================================================================================
# basic commands here
# ====================================================================================
 
def init_JY(com_port):
    # make sure the device manager is closed and the comport isn't open anywhere else
    # initialisation runs the spectrometer through the grating stops, and sets grating 1 (blaze 500) to what it thinks is 0nm. It also closes both of the slits
    print 'JY Horiba: monochromator initialized: COM '+ str(com_port)
    mono = instr.triax320(addr='COM'+str(com_port))
    
    return mono

def home_pos(mono,offset=-14107):
    print 'monochromator is going home...'
    # Initialisation runs the spectrometer through the grating stops, and sets grating 1 (blaze 500) to what it thinks is 0nm. 
    # It also closes both of the slits
    mono.motor_init()    
    # now we need to change the offset of the grating motors
    mono.bus.readall()
    mono.bus.write("G0,"+str(offset)+"\r")
    mono.wait_for_ok()
    mono.bus.readall()
    mono.bus.write("H\r")
    mono.wait_for_ok()
    mono.bus.readall()
    #now we need to open the slits
    mono._move_slit_relative(1,200) # entrance slit
    print 'entrance slit is at ', mono._get_slit_position(1)
    mono._move_slit_relative(2,200) # exit slit
    print 'exit slit is at ', mono._get_slit_position(2)
    print "Monochromator homing COMPLETE ---"
    return

def set_slits(mono,slit_enter,slit_exit):
    mono._set_slit_position(1,slit_enter) # entrance slit
    print 'entrance slit is at ', mono._get_slit_position(1)
    mono._set_slit_position(2,slit_exit) # exit slit
    print 'exit slit is at ', mono._get_slit_position(2)
    return

def get_slits(mono):
    while mono.is_busy():
        sleep(0.1)
    slits = [mono._get_slit_position(1),mono._get_slit_position(2)]
    print '(Enter,Exit)=',slits
    return slits

def read_wavelenth(mono):
    while mono.is_busy():
        sleep(0.050)
    wvlen = mono.get_wavelength()
    print 'wavelength =',wvlen
    return wvlen

def set_wavelength(mono,wvlen):
    if wvlen < 100 or wvlen > 1500:
        print 'ERROR: exceeds wavelength range'
        return 0
    else:
        mono.set_wl(wvlen) # or whatever you want, 542.4 and 628 @ 900lines per mm
        print 'wavelength is at ', mono.get_wl(), ' nm'
        return 1

def check_status(mono):
    # keep pinging at 2-sec intervals until the device is not busy
    
    return


# 8. Close JY device
def closeSG(mono):
    print 'JY Device closed'
    
# ====================================================================================
# higher level commands here
# ====================================================================================

def wavelen_scan(mono):
    print "do wavlen scan"
    return
#to do a wavelength scan (comment out the set_wl command above first to make sure we aren't creating backlash issues)
#for i in np.arange(515,580,1):
#   mono.set_wl(i)
#print 'you are at', i, ' nm, hit any key to continue', raw_input('')



# ----------------------- Main function below for testing ------------------
