# -*- coding: utf-8 -*-
"""
NewportPM3.py
** requries NewportPM_Setup.py to be saved in the same directory


adapted from NewportPM2.py (2014 version)
syntax updated from Python 2.7 to Python 3.7 (June 13,2019)

---
written by Yuzo Ishikawa
"""
import Newpma
import time

def initPM():
    stat = Newpma.Init_Sys()
    if stat != 0:
        print (stat)
        return stat;
    else:
        buff1=' '*32
        devinfo=Newpma.Get_DevInfo(buff1)
        devID=int(devinfo[0])
        print ("NewpPM: Poweter-meter initialized")
        return devID

def readPower(devID):
    #print '------'
    Newpma.Send_ASCII(devID,'PM:P?\r\n')
    buff1=' '*32
    time.sleep(0.1)
    npmout= Newpma.Get_ASCII(devID,buff1)
    #print npmout,type(npmout)
#    print ('------')
    digits = npmout.split('\r')[0]#.split('E')
    return digits
    #return float(digits[0])*(10**float(digits[1]))

def set_unit(devID,unit):
    diction = {0:"Amps",2:"Watts",3:"Watts/cm^2"}
    #diction = {0:"Amps",1:"Volts",2:"Watts",3:"Watts/cm^2   ",4:"Joules",5:"Joules/cm"}
    Newpma.Send_ASCII(devID,'PM:UNITS '+str(unit))
    print ('NewpPM: units set to '+diction[unit])
    return

def check_units(devID):
    #not working yet...
    print ('check units')
    return 'check units'

def zero(devID):
    Newpma.Send_ASCII(devID,'PM:ZEROSTO')
    print ('NewpPM: zerored at present reading')
    return

def beep(devID,beepONOFF):
    if beepONOFF == True:
        Newpma.Send_ASCII(devID,'PM:BEEP 1')
        print ('NewpPM: beep per measurement')
    else:
        Newpma.Send_ASCII(devID,'PM:BEEP 0')
        print ('NewpPM: no more beeping')
    return

def closePM():
    Newpma.Close_Sys()
    print ("NewpPM: PM2 Closed")
    return
