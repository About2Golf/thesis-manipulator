"""This program is the basic Python wrapper commands for the Sigma-Koki HIT stages (grating & camera)
 using the commands provided in the HIT Manual.

All commands are written to read degrees (translates to ticks when sending commands to HIT)
For reference: 1 deg = 40,000 ticks

alpha = grating angle from origin
beta = camera angle from origin 

Note: Our current use of "beta" terminology is incorrect.
Technically beta = (camera angle from origin) - alpha angle, but we will call (camera angle) = beta for simplicity.

Will require changing PORT # in init()


Created 22 Jul 2014

"""
import serial

# will need to determine this empirically

beta_limit = -60

# ----------------------- Commands for HIT stages ------------------

# 0. Initialize Stages for grating motion
#def init():
#hit = serial.Serial(port='COM4', baudrate=38400,parity=serial.PARITY_NONE,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE, timeout=1)
# add a check to see if really initialized

#    return hit

# 0. Initialize Stages for grating motion
# change the PORT value as needed
def init_hit(com_port):
#    hitdev = serial.Serial(port='COM'+ str(com_port), baudrate=9600,parity=serial.PARITY_NONE,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE, timeout=1)
    hitdev = serial.Serial(port='COM'+ str(com_port), baudrate=38400,parity=serial.PARITY_NONE,bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE, timeout=1)
    check_status = curr_pos(hitdev)
    if len(check_status) == 0:
        print 'SigmaKoki: Connection ERROR --> reconnect with SGSample'
        return -1
    else:
        print 'SigmaKoki: HIT device initialized: COM'+ str(com_port)
        return hitdev
        


# 1. Relative movement command from current position (moves to +/- X degrees)
def alpha_rel(hit,deg):
    conv=int(deg*40000)
    tick=str(conv)
    hit.write('M:,'+tick+'\r\n')
    print 'SigmaKoki: Grating moved '+str(deg)+' degrees ('+tick+ ' ticks)'
    
def beta_rel(hit,deg):
    conv=int(deg*40000)
    tick=str(conv)
    hit.write('M:'+tick+',\r\n')
    print 'SigmaKoki: Camera moved '+str(deg)+' degrees ('+tick+ ' ticks)'
    return

# 2. Absolute movement command from logical origin (moves to indicated degree)
# Will need to add a check to make sure grating holder doesn't run into camera (vice versa)
def alpha_abs(hit,deg):
    conv=int(deg*40000)
    tick=str(conv)
    hit.write('A:,'+tick+'\r\n')
#    print 'SigmaKoki: Grating moved to '+str(deg)+' degrees ('+tick+ ' ticks)'
    
def beta_abs(hit,deg):
    conv=int(deg*40000)
    tick=str(conv)
    hit.write('A:'+tick+',\r\n')
#    print 'SigmaKoki: Camera moved to '+str(deg)+' degrees ('+tick+ ' ticks)'
    return

# 3. Home stages (move back to mechanical origin)
# NOTE: Need to make sure stages are mechanical zeroing is completed first
# PREFERABLE NOT TO USE. INSTEAD SET ABSOLUTE MOTION TO 0

def home_all(hit):
    alpha_abs(hit,0)
    print (curr_pos(hit))
    print 'SigmaKoki: Homing complete'
    
def mhome_alpha(hit):
    hit.write('H:0,1\r\n')
    print 'SigmaKoki: Grating rotated to mechanical HOME'
    return
    
def mhome_beta(hit):
    hit.write('H:1,0\r\n')
    print 'SigmaKoki: Camera rotated to mechanical HOME'
    return

# 3b. Set logical Origin of both stages (to current mechancial position)
def set_origin(hit):
    hit.write('R:1,1\r\n')
    print 'SigmaKoki: Logical origin set'

# 4. Read current positions for both stages
# Output: 2D list of [degree, tick] (beta, alpha)
# to make sure readlines() doesn't go on infinitely, make sure timeout set to small time (eg 1 sec)
def curr_pos(hit):
    hit.write('Q:\r\n')
    lineList = hit.readlines()
    
    if lineList != []:
        outstr=lineList[-1].split(',')
        outstr= outstr[:2]
        cur_pos= [[float(s)/40000 for s in outstr],[float(s) for s in outstr]]
        return cur_pos
    else:
        return []
    
#below is the alpha, beta current positions reading after running curr_pos() above
# Output: [degree, tick]
def curr_alpha(hit):
    readout=[curr_pos(hit)[0][1], curr_pos(hit)[1][1]]
    print 'Grating pos: '+str(readout[0])+' deg ('+str(readout[1])+' ticks)'
    return readout
    
def curr_beta(hit):
    readout=[curr_pos(hit)[0][0], curr_pos(hit)[1][0]]
    print 'Camera pos: '+str(readout[0])+' deg ('+str(readout[1])+' ticks)'
    return readout

# 5. Abort current motion
def stop(hit):
    hit.write('L:E\r\n')
    print 'Emergency STOP'
    
# 6. Excite/Free motor (0 = excite off, 1 = excite on)dll.cs_Write(device,statement)
def free_motor(hit,state):
    if state == 1:
        hit.write('C:1,1\r\n')
        print 'SigmaKoki: Excitation on'
        return
    elif state == 0:
        hit.write('C:0,0\r\n')
        print 'SigmaKoki: Excitation off'
        return
    else:
        print 'SigmaKoki: Error: Incorrect input. Must be 0 or 1'
        return
   
# 7. Speed settings (change for all devices)
# start-up speed, max speed, acceleration/deceleration time
def speed(hit,spd):
    if spd == 1: #system default (need to change at every start-up?)
        hit.write('D:0,10000,100000,200\r\n')
        hit.write('D:1,10000,100000,200\r\n')
        print 'SigmaKoki: speed #1'
        return
    elif spd == 2:
        hit.write('D:0,30000,300000,200\r\n')
        hit.write('D:1,30000,300000,200\r\n')
        print 'SigmaKoki: speed #2'
        return
    elif spd == 3:
        hit.write('D:0,50000,500000,200\r\n')
        hit.write('D:1,50000,500000,200\r\n')
        print 'SigmaKoki: speed #3'
        return

# 8. Close HIT device
def closeSG(hit):
    hit.close()
    print 'SigmaKoki: HIT Device closed'

# ----------------------- Main function below for testing ------------------

def check_status(hit,wait=True):
    hit.write('!:\r\n')
    lineList=hit.readlines()
    outstre=lineList[-1].split(',')
    outstr=outstre[:2]
    out1,out2=int(outstr[1]),int(outstr[0])    
    return out1,out2
    
def get_systat(hit):
    hit.write('Q:S\r\n')
    print (hit.readlines() )
    

    
