
"""
===================================================================

   Scripts for the automated motion of the VPH grating test rig
   	
   Version: 2.1: 
   Written by: Y.Ishikawa 
   
   adapted from DESI scripts -> auto_scripts.py (version 1.x)
   which has been upgraded from Python 2.x to Python 3.x
   
   --------------------------------------------------
   update log
   
   June 14,2019 - created
   
   --------------------------------------------------
===================================================================
"""
import KPF_grating_GUI as kpf

#from scipy.interpolate import interp1d
from scipy import interpolate
import numpy as np
import time,os

global vxm
global hit
global npm
global jyh

global xx_data
global yy_data
global saveDir
global beta_minOK,beta_maxOK,alpha_minOK,alpha_maxOK
alpha_minOK = -55
alpha_maxOK = 110
beta_minOK = -30
beta_maxOK = kpf.safePos[4]

def init(sgh=[],nph=[],vxh=[],mon=[]):
    global hit
    global npm
    global jyh
    global vxm
    
    vxm = vxh
    hit = sgh
    npm = nph
    jyh = mon
    print ("KPF auto: initialized")
    return
    
def initDir(svdir):
    global saveDir
    saveDir=svdir
    return
    
def check_dataFile(searchDir,filename):
    fileList = []
    for file in os.listdir(searchDir):
        if file.endswith(".txt"):
            fileList.append(file)
    if filename in fileList:
        return True
    else:
        return False
   
def beta_calculator(alpha,wavelength,lineDensity,m_order=1):
    # solve the diffracted m-order according to the grating equation
    # [sin(beta)-sin(alpha)]=lineDensity*m_order*wavelength
    # by default m_order = +1, unless otherwise specified
    # line density in lines/mm --> this function will convert to lines per nm
    # wavelength in nm
    # alpha in degrees --> this function will convert
    beta = 0
    if alpha != 0:
        lineDensity = np.double(lineDensity)
        alpha = np.double(alpha)
        alpha_rad = np.deg2rad(alpha) # convert to radians
        N = np.divide(lineDensity , np.power(10,6)) # convert to lines per nm
        sinB = N*m_order*wavelength + np.sin(alpha_rad)
        beta = np.rad2deg(np.arcsin(sinB)) # solve B and convert to degrees
    phi = alpha-beta
    return phi,beta

# =======================================================================================
# medium-level stage motion (translation and rotation)
# - these include the software safetly limits and coordinate corrections
#   (defined in KPF_grating_GUI.py)
# - all motions defined here describe absolute positions
# - assumes that the coordinates have been calibrated and homed
# =======================================================================================
# OptoSigma rotation stages -----------------------
def alpha_move(deg,nowait=False):
    global vxm
    global hit
    global npm
    global alpha_minOK,alpha_maxOK
    print "SigmaKoki: Go to (alpha): "+str(deg)+" deg"
    
    # first check if OK to move
    if deg <= alpha_maxOK and deg >=alpha_minOK:
    # then check if ALHPA will run past the detector arm (cable collision danger)
        a_safe = sigko_checkSafe(deg,ALPHA=True,DEBUG=False)
        if a_safe != True:
            return False
        else:
            kpf.sigko.alpha_abs(hit,-deg)
            sigko_wait(nowait=nowait)
            return True
    else:
        print ("SigmaKoki: Exceeds allowed motion: ("+str(alpha_minOK)+' to '+str(alpha_minOK)+" deg)")
        return False
def beta_move(deg,nowait=False):
    global vxm
    global hit
    global npm   
    global beta_minOK,beta_maxOK
    
    print "SigmaKoki: Go to (beta): "+str(deg)+" deg"
    if deg <= beta_maxOK and deg >=beta_minOK:
        # then check if BETA will run past the ALPHA arm (cable collision danger)
        b_safe = sigko_checkSafe(deg,BETA=True,DEBUG=False)
        if b_safe != True:
            return False
        else:
            kpf.sigko.beta_abs(hit,-deg)
            sigko_wait(nowait=nowait)
            return True
    else:
        print ("SigmaKoki: Exceeds allowed motion: ("+str(beta_minOK)+' to '+str(beta_maxOK)+" deg)")
        return False

def sigko_wait(nowait=False):
    global hit
    sgstat = kpf.sigko.check_status(hit)
    if nowait == False:
        while sgstat != (0,0):
            sgstat = kpf.sigko.check_status(hit)
    return

# checks if OPTOSIGMA are safe to rotate with respect to each other
# motion is considered unsafe if
# (a) BETA and ALPHA are witin +/- 2 deg to each other; 
# (b) Final BETA or ALPHA crosses the current stage positions
def sigko_checkSafe(deg,ALPHA=False,BETA=False,DEBUG=False):
    okToMove = False
    
    # first, read in the current positions
    # convert the detector arm angle into ALPHA angle coordinates for easier comparision
    curpos    = sigko_positions()
    cur_alpha = curpos[0][1]
    cur_beta2 = (curpos[0][0]-90)
    degcheck  = deg
    
    # next, select the rotation arm to move
    cur_arm = ''
    cur_not = ''
    cur = ''
    arm_buff = 30
    convTobeta = 0
    buf1 = arm_buff
    buf2 = arm_buff
    if DEBUG != False:
        print 'current positions: ',cur_alpha,cur_beta2
    if ALPHA == True:
        cur = 'ALPHA'
        degcheck = deg
        convTobeta = 0
        cur_arm = cur_alpha
        cur_not = cur_beta2
        if DEBUG != False:
            print 'move: ',cur_alpha,' to ',degcheck
    if BETA == True:
        cur = 'BETA'
        degcheck = deg - 90
        convTobeta = 90
        cur_arm = cur_beta2
        cur_not = cur_alpha
        if DEBUG != False:
            print 'move: ',cur_beta2,' to ',degcheck
    buf1 = cur_not - arm_buff
    buf2 = cur_not + arm_buff
    if DEBUG != False:    
        print 'buffer regions: ',buf1+convTobeta,buf2+convTobeta
    # now check if OK to move
    okRange = ''
    
    if cur_arm < buf1 and degcheck > buf1:
        okRange = cur+' < '+str(buf1+convTobeta)
    elif cur_arm > buf2 and degcheck < buf2:
        okRange = cur+' > '+str(buf2+convTobeta)
    elif degcheck >= buf1 and degcheck <= buf2:
        if cur_arm < buf1:
#            okRange = str(buf1+convTobeta)+' < '+cur+' > '+str(buf2+convTobeta)
            okRange = str(buf1+convTobeta)+' < '+cu
        elif cur_arm > buf2:
            okRange = cur+' > '+str(buf2+convTobeta)
    else:
        okToMove = True
        
    if DEBUG != False:
        print 'checking...'
    
    if okToMove == False:
        print "SigmaKoki: DANGER! Alpha arm will run into the BETA arm!"
        print "SigmaKoki: Allowed positions: ("+okRange+" deg)"
    
    return okToMove
    

def sigko_positions():
    global hit
    curpos = kpf.sigko.curr_pos(hit)
    # beta
    curpos[0][1] = -curpos[0][1]
    curpos[1][1] = -curpos[1][1]
    # alpha
    curpos[0][0] = -curpos[0][0]
    curpos[1][0] = -curpos[1][0]
    
    return curpos

# Velmex translation stages -----------------------

def horiz_move(x_location):
    global vxm
    v3=x_location+kpf.stgCent[2]
    xLimit = 4.5
    if np.fabs(x_location) > xLimit:
        print 'VXM: horiz. exceeds safe motion. Must be x <= |'+str(xLimit)+'|'
    else:
        vxm.absoluteMove(3,0.5,v3)
        print 'VXM: Moving grating (horizontal) to ',x_location,' in'
    return -1 
    
def vert_move(y_location,detector=False,source=False):
    global vxm
    v1=y_location+kpf.stgCent[0]
    v2=y_location+kpf.stgCent[1]
    if detector == True:
        vxm.absoluteMove(1,1,v1)
        print 'VXM: Moving detector (vertical) to ',y_location,' in'
    if source == True:
        vxm.absoluteMove(2,1,v2)
        print 'VXM: Moving source (vertical) to ',y_location,' in'
    return

def vxm_positions(dev=0,detector=False,source=False,grating=False):
    global vxm
    if dev == 1 or detector == True:
        v1p = vxm.get_location(1)
        v1pi = -(v1p/4000.+kpf.stgCent[0])
        return v1pi,v1p
    elif dev == 2 or source == True:
        v2p = vxm.get_location(2)
        v2pi = -(v2p/4000.+kpf.stgCent[1])
        return v2pi,v2p
    elif dev == 3 or grating == True:
        v3p = vxm.get_location(3)
        v3pi = v3p/4000.-kpf.stgCent[2]
        return v3pi,v3p
    else:
        print "ERROR: can't get positions"
    return

def vxm_safeToMove(dev=0,detector=False,source=False,grating=False):
    okToMove = False
    if dev == 1 or detector == True:
        vpi,vp=vxm_positions(detector=True)
        if vpi > 5:
            okToMove = True
    elif dev ==2 or source == True:
        vpi,vp=vxm_positions(source=True)
        okToMove = True
    elif dev == 3 or grating == True:
        vpi,vp=vxm_positions(grating=True)
        if vpi >= -0.1 and vpi <= 0.1:
            okToMove = True
    return okToMove
    
# return the current positions of all the stages
def get_currPositions():
    v1i,v1 = vxm_positions(dev=1)
    v2i,v2 = vxm_positions(dev=2)
    v3i,v3 = vxm_positions(dev=3)
    sigpos = sigko_positions()
    alpha  = sigpos[0][1]
    beta   = sigpos[0][0]
    gratPos = [v1i,v2i,v3i,alpha,beta]
    return gratPos

# =======================================================================================
# Detector stuff
# =======================================================================================
def np_avgMeas(n):
    global npm
    measRec = []    
    for i in range (0,n):
        npread=float(kpf.np3.readPower(npm))
        measRec.append(npread)
    avgMeas=np.average(measRec)
    print ("** Avg Diode read: ",avgMeas)
    return avgMeas
    
def cntsMonit(tmax,fname=""):
    global saveDir
    print ("saving to :", fname)
    os.chdir(saveDir)
    tmin = tmax*60
    ff = open(fname+".txt",'ab')
    t0 = int(time.time())
    ti = t0
    tdiff = ti-t0
    while tdiff < tmin:
        if tdiff % 5:
            npread = np_avgMeas(3)
            ws = "{0:5d}   {1:10E}".format(ti,npread)
            ff.write(ws+"\n")
        ti = int(time.time())
        tdiff = ti-t0
    ff.close()
    print ("COMPLETE ---")
    return

# =======================================================================================
# now the higher-level code that runs the scripts using motion code defined above
# =======================================================================================
# to calibrate the stage positions -----
def home_rig():
    print 'Rig is going home...'
    global hit
    global vxm 
    # home the translation stages --> moves the stages to limit switches to calibrate positions
    # (Final positions: move vertical UP and the horizontal to the center)
    vxm.absoluteMove(1,1,12)
    vxm.set_home(1)
    vxm.absoluteMove(2,1,12)
    vxm.set_home(2)
    vxm.absoluteMove(3,0.5,-12)
    vxm.set_home(3)
    vxm.absoluteMove(3,0.5,kpf.stgCent[2])
    
    # then rotates the rotation stages to mechanical home to calibrate positions
    kpf.sigko.mhome_alpha(hit)    
    kpf.sigko.mhome_beta(hit)
    sgstat = kpf.sigko.check_status(hit)
    
    while sgstat != (0,0):
        sgstat = kpf.sigko.check_status(hit)
    kpf.sigko.speed(hit,2)

    # since the Optosigma mechanical home != logical home (tick marks), we must correct the 0.5 deg offset
    # (Final positions: offset + additional steps so grating is normal to beam, detector is in line with beam)    
    kpf.sigko.alpha_abs(hit,kpf.stgCent[3])
    kpf.sigko.beta_abs(hit,kpf.stgCent[4])
        
    sgstat = kpf.sigko.check_status(hit)
    while sgstat != (0,0):
        sgstat = kpf.sigko.check_status(hit)
    # reassign logical position as ZERO
    kpf.sigko.set_origin(hit)
    
    print "Rig homing COMPLETE ---"
    return

# this is just a repeat of the home_rig(), but partitioned for each motor controller-type
def reHome(sigma=False,velmex=False):
    global hit,vxm
    if sigma == True:
        # this is to home JUST the rotation stages; howver, the vertical stages MUST be re-positioned into safe positions to ensure safe rotation 
        vert_move(kpf.thruPos[0])
        horiz_move(0)
        print 'clear to move'
        # now rotate and home!
        kpf.sigko.mhome_alpha(hit)    
        kpf.sigko.mhome_beta(hit)
        sgstat = kpf.sigko.check_status(hit)
        while sgstat != (0,0):
            sgstat = kpf.sigko.check_status(hit)
        kpf.sigko.speed(hit,2)
        kpf.sigko.alpha_abs(hit,kpf.stgCent [3])
        kpf.sigko.beta_abs(hit,kpf.stgCent[4])
        sgstat = kpf.sigko.check_status(hit)
        while sgstat != (0,0):
            sgstat = kpf.sigko.check_status(hit)
        kpf.sigko.set_origin(hit)
        print "Optosigma Re-HOMED ---"
    elif velmex == True:
        # this will not care about the rotation stages, b/c it won't matter --> as long as the translation stages are moved in the right order
        vxm.absoluteMove(1,1,12)
        vxm.set_home(1)            
        vxm.absoluteMove(2,1,12)
        vxm.set_home(2)
        vxm.absoluteMove(3,0.5,-12)
        vxm.set_home(3)
        vxm.absoluteMove(3,0.5,kpf.stgCent[2])
        print "Velmex Re-HOMED ---"
    return

# scripts (motion) assuming that the stage positions are all calibrated -----

# goes to grating center
def goto_gratCenter(alpha=True,beta=True):
    print '* Going to Grating center...'
    aa=kpf.grtCent[3]
    bb=kpf.grtCent[4]
    horiz_move(kpf.grtCent[2])
    if vxm_safeToMove(dev=3) != True :
        vert_move(kpf.thruPos[0],detector=True)
    curpos = get_currPositions()
    if vxm_safeToMove(dev=3) == True:
        if alpha == True:
            if curpos[3] >= 45 and curpos[4] <= kpf.safePos[4]:
                beta_move(bb)    
                beta = False
            alpha_move(aa)
        if beta == True:
            beta_move(bb)
    else:
        print 'Warning: check grating position'
    vert_move(kpf.grtCent[0],source=True,detector=True)
    
    print "** Go to 'grating center': COMPLETE"
    return

# goes to grating center
def goto_thruBeam(alpha=True,beta=True):
    print '* Going to thru-Beam...'
    curpos = get_currPositions()
    aa=kpf.thruPos[3]
    bb=kpf.thruPos[4]
    vert_move(kpf.thruPos[1],detector=True,source=True)
    horiz_move(kpf.thruPos[2])
    if vxm_safeToMove(dev=3) == True:
        if alpha == True:
            if curpos[3] >= 45 and curpos[4] <= kpf.safePos[4]:
                beta_move(bb) 
                beta = False
            alpha_move(aa)
        if beta==True:
            beta_move(bb)
    else:
        print 'Warning: check grating position'
    print "** Go to 'thru-beam': COMPLETE"
    return

# goes to the 'safe' position (ideal for power-down procedure)
def goto_rigSafe():
    print '* Going to Safe position...'
    aa=kpf.safePos[3]
    bb=kpf.safePos[4]
    if vxm_safeToMove(dev=1) != True:
        vert_move(kpf.safePos[0],detector=True,source=True)
    horiz_move(kpf.safePos[2])
    if vxm_safeToMove(dev=3) == True:
        alpha_move(aa)
        beta_move(bb)    
    else:
        print 'Warning: check grating position'
    print "** Go to 'safe': COMPLETE"
    return

# =======================================================================================
# HIGH-level code that runs the main automated test scans 
# --> calls the motion scripts outlined above
# =======================================================================================
# wavelengh scans 
def waveScan(wave_param,intg_time,savefile,ff=[],GRATSWEEP=[],lineDensity=0,FIXEDPOS=True):
    currVert  = GRATSWEEP[0]
    currBeam  = GRATSWEEP[1]
    currHoriz = GRATSWEEP[2]
    currAlpha = GRATSWEEP[3]
    currPhi   = GRATSWEEP[4]
    currBeta  = currPhi
        
    for currWav in range(wave_param[0],wave_param[1]+wave_param[2],wave_param[2]):
        status = kpf.JYhoriba.set_wavelength(jyh,currWav)
        if status == 1:
            wv = np.float(currWav)
            if FIXEDPOS == False:
                calcPhi,calcBeta = beta_calculator(currAlpha,wv,lineDensity,m_order=1)
                currPhi  = calcPhi
                currBeta = calcBeta
            if kpf.noDetector != True:
                best_B,best_Y = maximize_flux(CUR_BETA=calcPhi,CUR_Y=currVert,BETA_SWEEP = True,VERT_SWEEP = True)
                if best_B == -999 and best_Y == -999:
                    print 'ERROR: cannot center beam\nERROR: Quitting'
                    return -1
                currPhi  = best_B[0]
                currVert = best_Y[0]
            else:
                beta_move(currPhi)
            currBeta = currPhi - currAlpha
            time.sleep(2)
            pw = np.float(np_avgMeas(intg_time))
            ts=int(time.time())
            time.sleep(2)
            ff = open(savefile,'ab')
            ws = "{0:12}   {1:4.0f}   {2:10E} ".format(ts,wv,pw)
            if GRATSWEEP !=[]:
                ws = "{0:12}   {1:4.0f}   {2:13E}   {3:7.3f}   {4:7.3f}   {5:7.3f}   {6:7.3f}   {7:7.3f}   {8:7.3f}".format(ts,wv,pw,currAlpha,currBeta,currPhi,currVert,currBeam,currHoriz)
            ff.write(ws+"\n")
            ff.close()
        else:
            print 'waveScan: ERROR with monochromator wavelength'
            return -1
        time.sleep(1)
    print '** Wavelength scan: COMPLETE'
    return 1

def beta_sweep(start_beta,step_size,n_steps,fileSave=[],interp=False,nmeas=3):
    bestpos,bestcnt,ok_cont=beta_scanner(start_beta,step_size,n_steps,mini_scan=interp,nmeas=nmeas)
    cntr=1
    max_cntr = 5
    while ok_cont is False:
        if cntr > max_cntr:
            print ("WARNING: beta-max position is NOT reliable, tried "+str(max_cntr)+" times. Force quit.")
            return bestpos,-1
        if interp == True:
            bestpos,bestcnt,ok_cont=beta_scanner(bestpos-0.2,step_size,n_steps,mini_scan=interp,nmeas=nmeas)
        else:
            bestpos,bestcnt,ok_cont=beta_scanner(bestpos-0.4,step_size,n_steps,mini_scan=interp,nmeas=nmeas)
        cntr+=1
        
    return bestpos,bestcnt


def beta_scanner(start_beta,step_size,n_steps,mini_scan=False,nmeas=3):#,noprint=False):
    global hit
    global npm
#    threshold = 0.05 #deg    
    
    beta_track = []
    phdo_track = []
    if step_size > 5:
        print ("ERROR: step size must be smaller than 5 deg!")
        return
    if n_steps< 3:
        print ("ERROR: must have more than 3 steps!")
        return
    for i in range(0,n_steps):
        goto_angle = (i)*step_size+start_beta
        beta_move(goto_angle)
        npread=np_avgMeas(nmeas)
        kpf.sigko.curr_pos(hit)
        beta_track.append(goto_angle)
        phdo_track.append(npread)
        
        print ('step: '+str(i),'angle: '+str((i+1)*step_size+start_beta))
        print (npread)
        print ('----------------------')
    bestpos,bestcnt = find_best(beta_track,phdo_track,step_size,threePoint=mini_scan)
    beta_move(bestpos)
    print ("SigKo: diff central: ",bestpos-beta_track[0])
    rat = np.divide(bestcnt,np.median(phdo_track))
    print ("SigKo: flux ratio: ",rat)
    if rat < 1.02:
#    if np.abs(bestpos-beta_track[0]) < threshold or np.abs(bestpos-beta_track[-1]) < threshold:
        ok_cont = False        
        return bestpos,bestcnt,ok_cont
    else:
        ok_cont = True
        return bestpos,bestcnt,ok_cont

def y_sweep(start_z,step_size,n_steps,nmeas):
    bestpos,bestcnt,ok_cont=y_scanner2(start_z,step_size,n_steps,nmeas)
    cntr=1
    max_cntr = 3
    while ok_cont is False:
        if cntr > max_cntr:
            print ("WARNING: beta-max position is NOT reliable, tried "+str(max_cntr)+" times. Force quit.")
            return bestpos,-1
        bestpos,bestcnt,ok_cont=y_scanner2(start_z-0.1,step_size,n_steps,nmeas)
        cntr+=1
    return bestpos,bestcnt

def y_scanner2(start_z,step_size,n_steps,nmeas):
    global npm   
    z_track = []
    phdo_track = []
    if step_size > 5:
        print ("ERROR: step size must be smaller than 5 deg!")
        return
    if n_steps< 4:
        print ("ERROR: must have more than 3 steps!")
        return
#    print (start_z)
    for i in range(0,n_steps+1):
        next_step=start_z+step_size*i
        z_track.append(next_step)
        vert_move(next_step,detector=True,source=False)
        npread=np_avgMeas(nmeas)
        phdo_track.append(npread)
        print (npread,next_step)
#    print (len(phdo_track),len(z_track))
    bestpos,bestcnt = find_best(z_track,phdo_track,step_size)    
    vert_move(bestpos,detector=True,source=False)
#    threshold = 0.1
    print ("VXM: diff central: ",bestpos-z_track[0])
    rat = np.divide(bestcnt,np.median(phdo_track))
    print ("VXM: flux ratio: ",rat)
    if rat < 1.02:
#    if np.abs(bestpos-z_track[0]) < threshold or np.abs(bestpos-z_track[-1]) < threshold:
        ok_cont = False        
        return bestpos,bestcnt,ok_cont
    else:
        ok_cont = True
        return bestpos,bestcnt,ok_cont

def maximize_flux(CUR_BETA=0,CUR_Y=0,BETA_SWEEP = True,VERT_SWEEP = True):
    bb_data = []
    yy_data = []
    nn = 3
    n_steps = 5
    if BETA_SWEEP == True:
        print " Maximizing flux: BETA angle"
        step_size = 0.2
        bestPos_b,bestCount_b = beta_sweep(CUR_BETA-0.4 ,step_size,n_steps,nmeas=nn,interp=False)
        if bestCount_b == -1:
            return -999,-999    
        bb_data = [bestPos_b,bestCount_b]
    if VERT_SWEEP == True:
        print " Maximizing flux: VERTICAL position"
        step_size = 0.05
        start_y = CUR_Y-step_size*3
        bestPos_y,bestCount_y = y_sweep(start_y-0.1,step_size,n_steps,nmeas=nn)
#        bestPos_y,bestCount_y = y_scanner(start_y-0.25,step_size,n_steps,nmeas=nn)
        yy_data = [bestPos_y,bestCount_y]
    
    print 'best detector pos: ',bb_data,yy_data
    print 'FLUX MAXIMIZE COMPLETE!'
    return bb_data,yy_data

def find_best(position,data,new_step,threePoint = False):
    global xx_data
    global yy_data
    if threePoint == True:
        print ("Do the 3 point interp" )
        new_step = new_step/10.
        xx = np.linspace(np.min(position),np.max(position),int(len(data)/np.fabs(new_step)))
        ff = interpolate.interp1d(position, data, kind='quadratic')
        yy = ff(xx)
        maxcount = np.max(yy)
        max_index = np.where(yy == maxcount)[0][0]
        best_pos = xx[max_index]
#        print (best_pos)
        best_pos=np.round(best_pos,decimals=5)
#        print (best_pos)
#        myy=np.median(yy)
#        rat = maxcount/myy
#        print (rat )
        print ("peak value: ",max_index,maxcount,best_pos)
        print ('---')
        #print xx
        #print '---------'
        #print yy
        
#        if rat < 1.05:
#            print ("**ERROR: did not scan through beam. Check initial position and scan range")
#        
        return best_pos,maxcount
    else:
        new_step = new_step/10.
        xx = np.linspace(np.min(position),np.max(position),int(len(data)/np.fabs(new_step)))
        ff = interpolate.interp1d(position, data, kind='cubic')
        yy = ff(xx)
        maxcount = np.max(yy)
        max_index = np.where(yy == maxcount)[0][0]
        best_pos = xx[max_index]
#        print (best_pos)
        best_pos=np.round(best_pos,decimals=5)
#        print (best_pos)
#        myy=np.mean(yy)
#        rat = maxcount/myy
#        print (rat )
        print ("peak value: ",max_index,maxcount,best_pos)
        print ('---')
        #print xx
        #print '---------'
        #print yy
#        
#        if rat < 1.05:
#            print ("**ERROR: did not scan through beam. Check initial position and scan range")
        
        return best_pos,maxcount

# script to find the best AOI
def bestAOI_test(wavelen,aoi,lineDensity,savefile):
    print 'saving to ',savefile
    aoiStart = aoi[0]
    aoiEnd   = aoi[1]
    
    df = aoiEnd-aoiStart
    stepDir = 1
    if df != 0:
        stepDir  = (df)/np.abs(df)        
    aoiStep = aoi[2]
     
    if np.sign(df) != np.sign(aoiStep):
        aoiStep *= stepDir
    aoiCurr = aoiStart

    # (0) Open file for data acquisition

    ab = open(savefile,'w')
    ab.write("{a:^10}{b:^10}{c:^10}{d:^10}{e:^10}{f:^10}{g:^10}{h:^10}".format(a="Timestamp",b="wavelength",c="power",d="alpha",e="beta",f="phi",g="detector",h="source",i="vph"))
    ab.write("\n")
    ab.write("{a:^10}{b:^10}{c:^10}{d:^10}{e:^10}{f:^10}{g:^10}{h:^10}".format(a="[Unix time]",b="[nm]",c="[Amp]",d="[deg]",e="[deg]",f="[deg]",g="[in]",h="[in]",i="[in]"))    
    ab.write("\n")
    ab.close()
    # (1) Thru beam at the beginning    
    goto_thruBeam(alpha=True)
    curPos = get_currPositions()
    eStat = waveScan(wavelen,5,savefile,ff=ab,GRATSWEEP=curPos,lineDensity=lineDensity)
    if eStat == -1:
        print 'AOI Test: ERROR with waveScan()\nQuitting!'
        return -1
    # (2) Move to grating center
    goto_gratCenter(alpha=False,beta=False)
    curPos = get_currPositions()
    y10 = curPos[0]
    y20 = curPos[1]
    xx0 = curPos[2]
    betCurr = curPos[3]
    # (3) Rotate the VPH and start the scan; loop through each AOI angle
    while (np.sign(aoiStep) == -1 and aoiCurr >= aoiEnd) or (np.sign(aoiStep) == 1 and aoiCurr <= aoiEnd):
        alpha_move(aoiCurr)
        curPos = [y10,y20,xx0,aoiCurr,betCurr]
        eStat = waveScan(wavelen,5,savefile,ff=ab,GRATSWEEP=curPos,lineDensity=lineDensity,FIXEDPOS=False)
        if eStat == -1:
            print 'AOI Test: ERROR with waveScan()\nQuitting!'
            return -1
        aoiCurr += aoiStep
    # (4) Finally go back to the thru beam for absolute calibration
    goto_thruBeam(alpha=True)
    curPos = get_currPositions()
    eStat = waveScan(wavelen,5,savefile,ff=ab,GRATSWEEP=curPos,lineDensity=lineDensity)
    if eStat == -1:
        print 'AOI Test: ERROR with waveScan()\nQuitting!'
        return -1
#    ab.close()
    print '** Best AOI scan: COMPLETE'
    return

def writeData(ff,savefile,wv,intg_time,positions):
    currAlpha = positions[3]
    currPhi   = positions[4]  
    currBeta  = currPhi - currAlpha
    currDet   = positions[0]
    currBeam  = positions[1]
    currHoriz = positions[2]
    pw = np.float(np_avgMeas(intg_time))
    ts=int(time.time())
    time.sleep(2)
    ws = "{0:12}   {1:4.0f}   {2:13E}   {3:7.3f}   {4:7.3f}   {5:7.3f}   {6:7.3f}   {7:7.3f}   {8:7.3f}".format(ts,wv,pw,currAlpha,currBeta,currPhi,currDet,currBeam,currHoriz)
    ff = open(savefile,'ab')    
    ff.write(ws+"\n")     
    ff.close()
    time.sleep(1)
    return


def fullGrating_sweep2(wavelen,bestAOI,lineDensity,scanParam,savefile,HORIZ=False,VERT=False,DIAG=False):
#    HORIZ = True
#    VERT  = True
#    DIAG  = True
    distFromCent = scanParam[0]
    scanStep = scanParam[1]
    print scanParam
    scanRange = [-distFromCent,distFromCent]
    
    # (0) Open the datafile to save
    ab = open(savefile,'w')
    ab.write("{a:^10}{b:^10}{c:^10}{d:^10}{e:^10}{f:^10}{g:^10}{h:^10}".format(a="Timestamp",b="wavelength",c="power",d="alpha",e="beta",f="phi",g="detector",h="source",i="vph"))
    ab.write("\n")
    ab.write("{a:^10}{b:^10}{c:^10}{d:^10}{e:^10}{f:^10}{g:^10}{h:^10}".format(a="[Unix time]",b="[nm]",c="[Amp]",d="[deg]",e="[deg]",f="[deg]",g="[in]",h="[in]",i="[in]"))    
    ab.write("\n")
    ab.close()
    # (1) Move to grating center at the best AOI and appropriate beta angle, and do a proxy scan
    goto_gratCenter(alpha=False,beta=False)
    alpha_move(bestAOI)
    curPos = get_currPositions()
    y10 = curPos[0]
    y20 = curPos[1]
    xx0 = curPos[2]
    aa0 = curPos[3]
    eStat = waveScan(wavelen,5,savefile,ff=ab,GRATSWEEP=curPos,lineDensity=lineDensity,FIXEDPOS=False)
    if eStat == -1:
        print 'Full Grating Test: ERROR with waveScan()\nQuitting!'
        return -1
    # =======================================================================================
    # (2) Now start the full grating scans in the order described below
    # set wavelength and do a full-grating scan in the order listed below
    #     (a) horizontal scan
    #     (b) vertical scan
    #     (c) diagonal scan #1
    #     (d) diagonal scan #2
    # =======================================================================================
    for currWav in range(wavelen[0],wavelen[1]+wavelen[2],wavelen[2]):
    # set the wavelength ----------------------------------------
        status = kpf.JYhoriba.set_wavelength(jyh,currWav)
        if status!=1:
            print 'JY Horiba: Monochromator wavelength ERROR\nQuitting!' 
            return -1
        # maximize the detector flux (cross maximize)
        wv = np.float(currWav)
        calcPhi,calcBeta = beta_calculator(aa0,wv,lineDensity,m_order=1)
        beta_move(calcPhi)
        if kpf.noDetector != True:
            best_B,best_Y = maximize_flux(CUR_BETA=calcPhi,CUR_Y=y10,BETA_SWEEP = True,VERT_SWEEP = True)
            if best_B == -999 and best_Y == -999:
                print 'ERROR: cannot center beam\nERROR: Quitting'
                return -1
            curPhi  = best_B[0]
            curVert = best_Y[0]
        else:
            beta_move(calcPhi)
            curPhi  = calcPhi
            curVert = y10 
        curPos  = [curVert,y20,xx0,aa0,curPhi]
        
        writeData(ab,savefile,currWav,5,curPos)
    # (2a) ----------------------------------------  
        if HORIZ == True:
            print 'horizontal scan...'
            xx = scanRange[0]
            while xx <= scanRange[1]:
                horiz_move(xx)
                curPos = [curVert,y20,xx,aa0,curPhi]
                writeData(ab,savefile,currWav,5,curPos)
                xx+=scanStep
            # do grating center scan ----------
            goto_gratCenter(alpha=False,beta=False)
            curPos = get_currPositions()
            y10 = curPos[0]
            y20 = curPos[1]
            xx0 = curPos[2]
            curPos = [y10,y20,xx0,aa0,curPhi]
            writeData(ab,savefile,currWav,5,curPos)
    # (2b) ----------------------------------------
        if VERT == True:
            print 'vertical scan...'
            yy = scanRange[0]
            while yy <= scanRange[1]:
                vert_move(yy,detector=True,source=True)
                curPos = [curVert,yy,xx0,aa0,curPhi] 
                writeData(ab,savefile,currWav,5,curPos)
                yy+=scanStep
            # do grating center scan ----------
            goto_gratCenter(alpha=False,beta=False)
            curPos = get_currPositions()
            y10 = curPos[0]
            y20 = curPos[1]
            xx0 = curPos[2]
            curPos = [y10,y20,xx0,aa0,curPhi]
            writeData(ab,savefile,currWav,5,curPos)
    # (2c) ----------------------------------------
        if DIAG == True:
            print 'diagonal scan #1...'
            xStep = scanStep*np.cos(np.pi/4)
            yStep = scanStep*np.sin(np.pi/4)
            rr = scanRange[0]
            xx = rr*np.cos(np.pi/4)
            yy = rr*np.sin(np.pi/4)
            while rr <= scanRange[1]:
                vert_move(yy,detector=True,source=True)
                horiz_move(xx)
                curPos = [curVert,yy,xx,aa0,curPhi] 
                writeData(ab,savefile,currWav,5,curPos)
                xx+=xStep
                yy+=yStep
                rr+=scanStep
            # do grating center scan ----------
            goto_gratCenter(alpha=False,beta=False)
            curPos = get_currPositions()
            y10 = curPos[0]
            y20 = curPos[1]
            xx0 = curPos[2]
            curPos = [y10,y20,xx0,aa0,curPhi]
            writeData(ab,savefile,currWav,5,curPos)
        # (2d) ----------------------------------------
            print 'diagonal scan #2...'
            xStep = -scanStep*np.cos(np.pi/4)
            yStep = scanStep*np.sin(np.pi/4)
            rr = scanRange[0]
            xx = -rr*np.cos(np.pi/4)
            yy = rr*np.sin(np.pi/4)
            while rr <= scanRange[1]:
                vert_move(yy,detector=True,source=True)
                horiz_move(xx)
                curPos = [curVert,yy,xx,aa0,curPhi] 
                writeData(ab,savefile,currWav,5,curPos)
                xx+=xStep
                yy+=yStep
                rr+=scanStep
            # do grating center scan ----------
            goto_gratCenter(alpha=False,beta=False)
            curPos = get_currPositions()
            y10 = curPos[0]
            y20 = curPos[1]
            xx0 = curPos[2]
            curPos = [y10,y20,xx0,aa0,curPhi]
            writeData(ab,savefile,currWav,5,curPos)
    # =======================================================================================
    # (3) return to grating center for best AOI and do a wavelength scan
    goto_gratCenter(alpha=False,beta=False)
    eStat = waveScan(wavelen,5,savefile,ff=ab,GRATSWEEP=curPos,lineDensity=lineDensity,FIXEDPOS=False)
    if eStat == -1:
        print 'Full Grating Test: ERROR with waveScan()\nQuitting!'
        return -1
    
    print 'FULL GRATING FINISHED'
    return 1
