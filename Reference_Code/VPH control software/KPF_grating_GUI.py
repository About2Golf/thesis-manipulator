"""
===================================================================

   GUI for KPF VPH grating rig
   calls commands and data acquired by:
	
   Version: 2.2: 
   Written by: Y.Ishikawa 
   
   adapted from DESI_grating_GUI.py (version 1.x)
   
   --------------------------------------------------
   update log
   
   June 11,2019 - created
   June 20,2019 - downgraded to Python 2.7   
   
   --------------------------------------------------
===================================================================
"""

#import Python libraries and other useful libraries
import os,sys
import kpf_misc
#import the lower-level modules
from vxm_class3 import *
import JYHoriba_mono as JYhoriba
import SigKo_Grating3 as sigko
import NewportPM3 as np3
#from auto_scripts import *
import kpf_automation_scripts as kauto

from PyQt4 import QtGui,QtCore
import math
import numpy as np
global mainGUI
# preset positions 
global grtCent,thruPos,safePos,stgCent
from datetime import datetime

# this is for debugging
global noDetector
noDetector = True

# the absolute stage positions from the limit switches to get to grating center
c_source  = -7.76 # from top limit switch
c_detect  = -6.64 # from top limit switch
c_grating = 4     # from left limit switch
os_offset = 1.5   # to correct for the 
c_alpha   = os_offset+45+90 # rotate to "good" locations so that we can move in positive and negative angles
c_beta    = os_offset+74.55
stgCent = [c_detect,c_source,c_grating,c_alpha,c_beta]

# relative coordinates w.r.t. grating center (0,0,0,0,0)
grtCent = [0,0,0,0,0]
thruPos = [5.65,5.8,0,0,0]
safePos = [6,7.5,0,90,45]
todayDate = datetime.today().strftime('%Y-%m-%d')

class KPF_VPH_GUI(QtGui.QMainWindow):
    # ----------------------------------------------------------------------------------------------------------------------------------
    # Initialize the GUI window and defines the parameters
    # ----------------------------------------------------------------------------------------------------------------------------------
    # Set global variables and constants -----------------------------------------------    
    global osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI,cmGUI
    global vxm,hit,npm,jyh
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global aoi_ScanParam,fullgrat_ScanParam
    btnX = 200
    btnY = 50
    frameSpace = 20
    menuSize = 20
    btnSpace = 10
    
    global JY_COM,SIG_COM,VXM_COM
    SIG_COM = 1
    VXM_COM = 16
    JY_COM  = 9
    
    global homeDir,saveDir
    homeDir = os.getcwd()
    saveDir = os.getcwd()+'\\test'
    
    global progStat,conErrText,txtFirst
    progStat = False
    txtFirst = True
    conErrText = "ERROR: NOT conneted to devices. Did you click 'Connect Devices'?"
        
    global pmUnit
    pmUnit = "Amp"
    
    global grtCent,thruPos,safePos
    
    # VPH settings
    global greenVPH,redVPH,todayDate,VPH_clearAperture
    g_lineDensity = 810
    r_lineDensity = 450
    g_waveRange   = [445,600] #nm
    r_waveRange   = [600,870] #nm
    waveStep      = 10 #nm
    aoiGreen      = [-28,-32] #deg
    aoiRed        = [-22,-26] #deg
    aoiStep       = 0.5 #deg
    fullGratScan  = 2 #in
    fullGratStep  = 0.1
    VPH_clearAperture = 4.
    greenName     = todayDate+'_green_'
    redName       = todayDate+'_red_'
    greenVPH = [g_lineDensity,g_waveRange,waveStep,aoiGreen,aoiStep,greenName,fullGratScan,fullGratStep]
    redVPH   = [r_lineDensity,r_waveRange,waveStep,aoiRed,aoiStep,redName,fullGratScan,fullGratStep]
    
    # -------------------------------------------------------------------------------
    
    
    def __init__(self):
        super(KPF_VPH_GUI,self).__init__()
        self.title='KPF - VPH testing rig control panel'
        self.left=200
        self.top=200
        self.width=920
        self.height=500
        
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        self.setFont(QtGui.QFont("Arial",10))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.center()
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        self.statusBar().showMessage('Initializing...',1000)

        # menu bar stuff --------------------------------------
        menubar = self.menuBar()
        
        comMenu = menubar.addMenu("&Connections")
        comMenu.setStyleSheet("background-color: cyan")
        comMenu.addAction("&Open devices",self.gui_init)
        comMenu.addAction("&Kill connections",self.gui_killALL)
        # change the directory information
        menubar.addAction("&Change save directory",self.dataSave)
        # Control each device individually        
        fileMenu = menubar.addMenu("&Go to device(s)")
        fileMenu.addAction("&OptoSigma controls",self.openGui2)
        fileMenu.addAction("&Velmex controls",self.openGui3)
        fileMenu.addAction("&PowerMeter controls",self.openGui4)
        fileMenu.addAction("&JY Horiba controls",self.openGui5)
        # troubleshooting
        menubar.addAction("&Help (Open manual)",self.trblshoot)
        # get information about the GUI program
        menubar.addAction("&About",self.about)  
        
        # start inserting the GUI buttons here ------------
        self.show_all_buttons()
        self.update_display(COM=False,mono=False,sigma=False,newp=False,linstage=False,curSavDir=False)
        
        self.show()
    # ----------------------------------------------------------------------------------------------------------------------------------
    #   Define button triggers: (i.e. "If click detected ---> then run action-program")
    # ---------------------------------------------------------------------------------------------------------------------------------- 
    
    # Miscellaneous (formatting and menu bar) programs --------------------------------
    def notConnect(self):
        global conErrText
        print conErrText 
        self.statusBar().showMessage(conErrText,15000)
         
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # menuDropdown for additional connections --
    def openGuiA(self):
        QtGui.QMessageBox.about(self, "blah","""Get device status""")
    
#        QtGui.QMessageBox.about(self, "Select custom tests","""In progress.....""")
    def about(self):
        global saveDir
        QtGui.QMessageBox.about(self, "About","Keck Planet Finder\n----------------\nPython GUI for VPH grating measurements\nadapted from DESI_grating_GUI.py\nin Python 2.7\n----\nWritten by: Yuzo Ishikawa\n----\nData save to:\n"+saveDir)
    # control each device --
    def openGui2(self):
        osGUI.show()
    def openGui3(self):
        vxGUI.show()
    def openGui4(self):
        QtGui.QMessageBox.about(self, "Newport","""Open Newport powermeter""")
    def openGui5(self):
        jyGUI.show()
    # automated programing --
    def openGui7(self):
        fgGUI.show()
#        QtGui.QMessageBox.about(self, "Run: full grating scan","""program the automation yourself""")
    def openGui8(self):
        QtGui.QMessageBox.about(self, "Run: wavelength scan (fixed position)","""program the automation yourself""")

    
    def comm_Param(self):
        print "blha"
        
    def trblshoot(self):
        global homeDir
        cc = os.getcwd()
        os.chdir(homeDir)
        openManual = "start VPH_python_GUI.pdf"
        os.system(openManual)
        os.chdir(cc)
        return
    
    def dataSave(self):
        global homeDir
        global saveDir
        dd = QtGui.QFileDialog.getExistingDirectory(self, 'Select a folder:',homeDir, QtGui.QFileDialog.ShowDirsOnly)
        if len(dd) != 0 :
            saveDir=str(dd)
            os.chdir(saveDir)
            showText = 'save directory changed to: '+saveDir
            if txtFirst != True:
                self.update_display(curSavDir=True)
        else:
            showText = 'save directory NOT changed. \n'+saveDir
        
        print showText 
        self.statusBar().showMessage(showText,3000)
        
    # Real programs ------------------------------------------------------------------------------------------------
    def show_all_buttons(self):
        global btnSpace,btnX,btnY,menuSize,frameSpace
        global initBtn,progStat
        # connect --------
        nx = 0
        ny = 0
        homeBtn = QtGui.QPushButton('Home ALL (calibrate)', self)
        homeBtn.resize(btnX,btnY)
        homeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                     frameSpace+btnY*ny+menuSize+btnSpace*ny)
        homeBtn.setToolTip('Click to HOME ALL devices')
        homeBtn.released.connect(self.gui_homeAll)
        
        # close all -------------
#        nx = 1
#        ny = 0
#        closeBtn = QtGui.QPushButton('Close connections', self)
#        closeBtn.resize(btnX,btnY)
#        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
#                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
#        closeBtn.setToolTip('Click to Kill ALL device connections')
#        closeBtn.released.connect(self.gui_killALL)
        
        # go to home------------
        nx = 0
        ny = 1
        homeBtn = QtGui.QPushButton('Thru-beam', self)
        homeBtn.resize(btnX,btnY)
        homeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                     frameSpace+btnY*ny+menuSize+btnSpace*ny)
        homeBtn.setToolTip('Click to HOME ALL devices')
        homeBtn.released.connect(self.gui_beamTHRU)
        
        # go to home------------
        nx = 0
        ny = 2
        homeBtn = QtGui.QPushButton('Beam VPH centerline', self)
        homeBtn.resize(btnX,btnY)
        homeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                     frameSpace+btnY*ny+menuSize+btnSpace*ny)
        homeBtn.setToolTip('Click to HOME ALL devices')
        homeBtn.released.connect(self.gui_beamOCL)
        
        # go to home------------
        nx = 0
        ny = 3
        homeBtn = QtGui.QPushButton('Safe position (end)', self)
        homeBtn.resize(btnX,btnY)
        homeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                     frameSpace+btnY*ny+menuSize+btnSpace*ny)
        homeBtn.setToolTip('Shutdown: move to safe position')
        homeBtn.released.connect(self.gui_rigSafe)

    # General status ---------------------------------------
        # get all positions
        nx = 1
        ny = 1
        closeBtn = QtGui.QPushButton('Get current positions', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('Current stage positions: monochromator, rotation, and linear stages')
        closeBtn.released.connect(self.gui_status)
        
    # Monochroomator stuff ---------------------------------------
        # set wavelength 
        nx = 1
        ny = 2
        closeBtn = QtGui.QPushButton('Set wavelength (nm)', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('set wavelength')
        closeBtn.released.connect(self.gui_setWvln)
        # set slit width 
        nx = 1
        ny = 3
        closeBtn = QtGui.QPushButton('Set slits width', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('set slit width')
        closeBtn.released.connect(self.gui_setslits)
        
    # Newport powermeter stuff ---------------------------------------
        nx = 2
        ny = 0
        closeBtn = QtGui.QPushButton('Max counts', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('Move detector (rotate and translate) to maximize counts')
        closeBtn.released.connect(self.gui_maxCounts)        
        
        nx = 2
        ny = 1
        closeBtn = QtGui.QPushButton('Zero PM', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('Re-zero detector')
        closeBtn.released.connect(self.gui_zeroPM)
        
        # Detector get reading
        nx = 2
        ny = 2
        closeBtn = QtGui.QPushButton('Get PM reading', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('get instantaneous reading ')
        closeBtn.released.connect(self.gui_pwmRead)
        
        # Detector get reading
        nx = 2
        ny = 3
        closeBtn = QtGui.QPushButton('Set PM units', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('get instantaneous reading ')
        closeBtn.released.connect(self.gui_pwmUnits)
        
        # best alpha test -------------
        nx = 3
        ny = 0
        closeBtn = QtGui.QPushButton('RUN: Best AOI test', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('Click to run automation')
        closeBtn.released.connect(self.gui_best_AOI)
        
        # full grating test -------------
        nx = 3
        ny = 1
        closeBtn = QtGui.QPushButton('RUN: Full grating scan', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('Click to run automation')
        closeBtn.released.connect(self.gui_full_scan)
    
        # full grating test -------------
        nx = 3
        ny = 2
        closeBtn = QtGui.QPushButton('RUN: wavelength scan', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('Click to run wavelength scan')
        closeBtn.released.connect(self.gui_wvlen_scan)
        
        # best alpha test -------------
        nx = 3
        ny = 3
        closeBtn = QtGui.QPushButton('RUN: Custom test', self)
        closeBtn.resize(btnX,btnY)
        closeBtn.move(frameSpace+btnX*nx+btnSpace*nx,
                      frameSpace+btnY*ny+menuSize+btnSpace*ny)
        closeBtn.setToolTip('Click to create and run custom scan')
        closeBtn.released.connect(self.openGuiB)
        
        
        
        return
    # ----------------------------------------------------------------------------------------------------------------------------------
    #   Define button triggers: (i.e. "If click detected ---> then run action-program")
    # ---------------------------------------------------------------------------------------------------------------------------------- 
    
    def gui_init(self):
        global JY_COM,SIG_COM,VXM_COM
        print '====================================='
        print '*GUI: Connecting to devices...'
        print '====================================='
        self.statusBar().showMessage('Connecting to devices...',1000)
        global vxm,hit,npm,jyh
        global initBtn,progStat,txtFirst,saveDir
        noError = self.set_COM()
        
        if noError == True:
            vxm = vxm_controller3(VXM_COM,3)
            print '---'
            jyh = JYhoriba.init_JY(JY_COM)        
            print '---'
            npm = np3.initPM()   
            np3.beep(npm,False)
            print '---'
            hit = sigko.init_hit(SIG_COM)
            if hit == -1:
                print 'ERROR: quitting'
                return
            print '---'
            os.chdir(saveDir)
            kauto.init(sgh=hit,nph=npm,vxh=vxm,mon=jyh)
            print '---'
            self.statusBar().showMessage('Devices connected!',1000)
            progStat = True
            self.update_display(COM=True,mono=True,sigma=True,newp=True,linstage=True,curStat='Status: connected')
            txtFirst = False
#        print 'REAL grating center: ', stgCent
        print '====================================='
#        kpf_misc.printout('*GUI: Device initialization COMPLETE!',kpf_misc.GREEN)
        print '*GUI: Device initialization COMPLETE!'
        print '====================================='
        return
    
    # This doesn't work right now....
    def gui_killALL(self):
        global initBtn,progStat
        self.statusBar().showMessage('Closing devices',5000)
        print "KILL ALL DEVICES" 
        self.update_display(curStat='Status: disconnected')
        progStat = False
        return
    
    def set_COM(self):
        global VXM_COM,JY_COM,SIG_COM,progStat
        VXM_old = VXM_COM
        JY_old = JY_COM
        SIG_old = SIG_COM
        k, ok_VXM = QtGui.QInputDialog.getInt(self, "Velmex (Linear stages) COM Port","COM (Default/current = "+str(VXM_COM)+"):", VXM_COM, 0, 20, 1)
        i, ok_JYH = QtGui.QInputDialog.getInt(self, "JY Horiba (Monochromator) COM Port","COM (Default/current = "+str(JY_COM)+"):", JY_COM, 0, 20, 1)
        j, ok_SIG = QtGui.QInputDialog.getInt(self, "SigmaKoki (Rotation stage) COM Port","COM (Default/current = "+str(SIG_COM)+"):", SIG_COM, 0, 20, 1)
#        print 'COM check  (Velmex,JY,SigKo): ',ok_VXM,ok_JYH,ok_SIG
        if ok_VXM:
            VXM_COM = k
            print 'COM =',k,'(Velmex)'
        if ok_JYH:
            JY_COM = i
            print 'COM =',i,' (JY Horiba)' 
        if ok_SIG :
            SIG_COM = j
            print 'COM =',j,' (SigmaKoki)' 
        conStat = True
        if ok_VXM == False and  ok_JYH == False and ok_SIG == False:
            conStat = False
        else:
            if progStat == True and (VXM_old != VXM_COM and JY_old != JY_COM and SIG_old != SIG_COM):
                self.statusBar().showMessage('Mono COM: '+str(i)+' , SigmaKoki COM:'+str(j)+' --> COM changed! RESTART PROGRAM and re-connect',50000)
            else:
                self.statusBar().showMessage('Mono COM: '+str(i)+' , SigmaKoki COM:'+str(j),5000)
        print '--------------'
        return conStat
    
    def gui_homeAll(self):
        global progStat,conErrText
        global vxm,hit,npm,jyh
        if progStat == True:
            self.statusBar().showMessage('Stages: going home...',5000)
            kauto.home_rig()
            self.statusBar().showMessage('Mono: going home...',5000)
            JYhoriba.home_pos(jyh)
            self.update_display(mono=True,sigma=True,linstage=True,newp=True)
            print '====================================='
            print '*GUI: Home ALL COMPLETE!'
            print '====================================='
        else:
            self.notConnect()
#        self.update_display(curStat='Status: COMPLETE')
        return
    
    def gui_beamTHRU(self):
        global progStat,conErrText
        if progStat == True:
            self.statusBar().showMessage('THRU BEAM~',5000)
            kauto.goto_thruBeam(alpha=True)
            self.update_display(linstage=True)
            print '====================================='
            print '*GUI: Thru-Beam COMPLETE!'
            print '====================================='
        else:
            self.notConnect()
        return
    
    def gui_beamOCL(self):
        global progStat,conErrText
        if progStat == True:
            self.statusBar().showMessage('Grating center line~',5000)
            kauto.goto_gratCenter()
            self.update_display(linstage=True)
            print '====================================='
            print "*GUI: Beam VPH centerline COMPLETE!"
            print '====================================='
        else:
            self.notConnect()
        return
    
    def gui_rigSafe(self):
        global progStat,conErrText
        if progStat == True:
            self.statusBar().showMessage('Moving to safe position (VPH center, sensors up, arm away)',5000)
            kauto.goto_rigSafe()
            print '====================================='
            print '*GUI: Safe position (end) COMPLETE!'
            print '====================================='
        else:
            self.notConnect()
        return
# =======================================================================================================================
# run the main automation scripts
# program will confirm with user about parameters first
# =======================================================================================================================
    def gui_maxCounts(self):
        global progStat
        if progStat == True:
            curpos  = kauto.sigko_positions()
            beta    = curpos[0][0]
            v1i,v1  = kauto.vxm_positions(dev=1)
            best_B,best_Y = kauto.maximize_flux(CUR_BETA=beta,CUR_Y=v1i,BETA_SWEEP = True,VERT_SWEEP = True)
            if best_B == -999 and best_Y == -999:
                print 'ERROR: cannot find beam'
        else:
            self.notConnect()
        return

    def gui_best_AOI(self):
        global progStat,conErrText
        global osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI,cmGUI
        global aoi_ScanParam
        if progStat == True:
            a0GUI.show()
#            kauto.alpha_beta()
            #(a_0,a_fin,a_step,b_0,b_step,nmeas,vloc=[-7.03,-8.11,-3.25],wave=500,filename="alpha_beta")
        else:
            self.notConnect()
        
        self.update_display(curStat='Status: COMPLETE')
        return
    
    def gui_full_scan(self):
        global osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI,cmGUI
        
        global progStat,conErrText
        if progStat == True:
            fgGUI.show()
#            self.update_display(curStat='Status: Running Full grating scan')
        else:
            self.notConnect()
#        self.update_display(curStat='Status: COMPLETE')
        return
        
    def openGuiB(self):
        global osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI,cmGUI
        if progStat == True:
            cmGUI.show()
            self.statusBar().showMessage('Custom scans',10000)
#            self.update_display(curStat='Status: Running Full grating scan')
        else:
            self.notConnect()
#        self.update_display(curStat='Status: COMPLETE')
        return
        
        
    def gui_wvlen_scan(self):
        global osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI,wvGUI,cmGUI
        global progStat
        if progStat == True:
            wvGUI.show()
        else:
            self.notConnect()
        self.update_display(curStat='Status: COMPLETE')
        return
# =======================================================================================================================  
    
    def gui_setWvln(self):
        global progStat,conErrText
        if progStat == True:
            wvlen, OKPress = QtGui.QInputDialog.getInt(self,"Wavelength set", "Enter wavelength (nm)", 500, 0,15000, 1)
            if OKPress:
                self.statusBar().showMessage('Set wavelength to '+str(wvlen)+' nm',10000)
                status = JYhoriba.set_wavelength(jyh,wvlen)
                if status == 1:
                    self.update_display(mono=True)
                else:
                    self.statusBar().showMessage('ERROR: exceeds wavelength range',10000)
        else:
            self.notConnect()
        return
    
    def gui_setslits(self):
        global progStat
        if progStat == True:
            entr_slit, OKPress1 = QtGui.QInputDialog.getInt(self,"Slit set", "Entrance slit (nm)", 100, 0,15000, 1)
            exit_slit, OKPress2 = QtGui.QInputDialog.getInt(self,"Slit set", "Exit slit (nm)", 200, 0,15000, 1)
            if OKPress1 or OKPress2:
                self.statusBar().showMessage('Set slits [nm]: Entrance --> '+str(entr_slit)+' , Exit --> '+str(exit_slit),10000)
                JYhoriba.set_slits(jyh,entr_slit,exit_slit)
                self.update_display(mono=True)
        else:
            self.notConnect()
        return
    
    def gui_pwmRead(self):
        global progStat
        if progStat == True:
            self.statusBar().showMessage('Getting detector reading',5000)
            self.update_display(newp=True)
        else:
            self.notConnect()
        return
    
    def gui_zeroPM(self):
        global progStat
        global npm
        if progStat == True:
            self.statusBar().showMessage('Zeroing detector',5000)
            np3.zero(npm)
            print "COMPLETE ---"
        else:
            self.notConnect()
        return
    
    def gui_pwmUnits(self):
        global progStat
        global npm,pmUnit
        items = ("Amp","Watts","Watts/cm^2")
        units = {items[0]:0,items[1]:1,items[2]:2}
        if progStat == True:
            item, okPressed = QtGui.QInputDialog.getItem(self, "Set PM units","Select units (default = Amps):", items, 0, False)
            pmUnit = item
            if okPressed:
                self.statusBar().showMessage('Unit selected: '+item,5000)
                np3.set_unit(npm,units[str(pmUnit)])
                self.update_display(newp=True)
        else:
            self.notConnect()
        return
    
       
    def gui_status(self):
        global progStat
        if progStat == True:
            self.update_display(mono=True,sigma=True,linstage=True)
        else:
            self.notConnect()
        return
    
    def update_display(self,COM=False,mono=False,sigma=False,newp=False,linstage=False,curStat='',curSavDir=True):
        global mainGUI
        global progStat,txtFirst,saveDir
        global VXM_COM,JY_COM,SIG_COM,npm
        global stgCent
        global txt0,txt1,txt2,txt3,txt4,txt5,txt6,txt7,txt8,txt9,txt10,txt11,txt12,txt13,txtxx,txtsv
        global pmUnit
        global vxm,hit,npm,jyh
        if txtFirst == True:
            txt0=[]
            txt1=[]
            txt2=[]
            txt3=[]
            txt4=[]
            txt5=[]
            txt6=[]
            txt7=[]
            txt8=[]
            txt9=[]
            txt10=[]
            txt11=[]
            txt12=[]
            txt13=[]
            txtxx=[]
            txtsv=[]
            
#        print mono,sigma,linstage,newp
        # device status
        if COM == True:
            txt0 = self.show_text("Velmex     : COM "+str(VXM_COM),nx=0,ny=4.5,textObj=txt0)
            txt1 = self.show_text("SigmaKoki : COM "+str(SIG_COM),nx=0,ny=5.5,textObj=txt1)
            txt2 = self.show_text("JY Horiba  : COM "+str(JY_COM),nx=0,ny=5,textObj=txt2)
            txt13 = self.show_text("Newport  : devID "+str(npm),nx=0,ny=6,textObj=txt13)
        # monochromator
        if mono == True:
            curSlits = JYhoriba.get_slits(jyh)
            curWvlen = JYhoriba.read_wavelenth(jyh)
            txt3 = self.show_text("wavelength : "+str(curWvlen)+" nm",nx=0.8,ny=4.5,textObj=txt3)
            txt4 = self.show_text("Slit (enter)  : "+str(curSlits[0])+" um",nx=0.8,ny=5,textObj=txt4)
            txt5 = self.show_text("Slit (exit)    : "+str(curSlits[1])+" um",nx=0.8,ny=5.5,textObj=txt5)
        # Newport detector
        if newp == True:
            pw = np3.readPower(npm)
            txt6 = self.show_text("Detector cnts : "+str(pw)+" "+pmUnit,nx=1.83,ny=4.5,textObj=txt6)
            txt7 = self.show_text("Units : "+pmUnit,nx=1.83,ny=5,textObj=txt7)
        # OptoSigma
        if sigma == True:
#            curpos = sigko.curr_pos(hit)
            curpos = kauto.sigko_positions()
            txt8 = self.show_text("alpha (VPH)   : "+str(curpos[0][1])+" deg  ("+str(curpos[1][1])+")",nx=3,ny=4.5,textObj=txt8)
            txt9 = self.show_text("beta (sensor) : "+str(curpos[0][0])+" deg  ("+str(curpos[1][0])+")",nx=3,ny=5,textObj=txt9)
        # velmex stages
        if linstage == True:
            vxm1i,vxm1 = kauto.vxm_positions(dev=1)
            vxm2i,vxm2 = kauto.vxm_positions(dev=2)
            vxm3i,vxm3 = kauto.vxm_positions(dev=3)
            txt10 = self.show_text("Y1 (sensor) : "+str(vxm1i)+"  in    ("+str(vxm1)+")",nx=3,ny=5.5,textObj=txt10,custSize=[2.5,1])
            txt11 = self.show_text("Y2 (source) : "+str(vxm2i)+"  in    ("+str(vxm2)+")",nx=3,ny=6,textObj=txt11,custSize=[2.5,1])
            txt12 = self.show_text("X  (grating) : "+str(vxm3i)+" in  ("+str(vxm3)+")",nx=3,ny=6.5,textObj=txt12,custSize=[2.5,1])
        if curStat != '':
            txtxx = self.show_text(curStat,nx=0,ny=6.75,textObj=txtxx)
        if curSavDir == True:
            txtsv = self.show_text('Save Dir: '+saveDir,nx=0.8,ny=6.5,textObj=txtsv,custSize=[2.5,1])

        if COM != False or  mono != False or newp  != False or sigma  != False or linstage != False or curStat != '':
            print '---'
#            print('*GUI: Display panel updated')
#            print('--------------------------------')
        return
    
    def show_text(self,theText,nx=1,ny=4,textObj=[],custSize=[1.5,1]):
        global txtFirst 
        if txtFirst == True or textObj == []:
            textObj = QtGui.QLabel(theText,self)
        
        textObj.move(frameSpace+btnX*nx+btnSpace*nx+10,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        textObj.setText(theText)
        textObj.resize(btnX*custSize[0]+20,btnY*custSize[1]/2)
        textObj.show()
        return textObj
        
# **********************************************************************************************************************************
# Run the AUXILIARY GUI program
# ********************************************************************************************************************************** 
# **********************************************************************************************************************************
#   Debugging windows for OptoSigma, Velmex, and Powermeter   
# **********************************************************************************************************************************
class optSg_Window(QtGui.QWidget):
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global mainGUI,osGUI,vxGUI,pmGUI    
    global vxm,hit,npm,jyh
    
    def __init__(self):
        xsize=450
        ysize=300
        global xcnst
        global ycnst
        xcnst=1.5
        ycnst=0.5
        super(optSg_Window,self).__init__()
        self.setWindowTitle("OptoSigma controls") 
        self.setGeometry(300,50,xsize,ysize)
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        self.osButtons()
        
    def osButtons(self):
        nx = 0
        ny = 0
        btn1 = QtGui.QPushButton('Reconnect', self)
        btn1.setStyleSheet("background-color:purple;border")
        btn1.resize(btnX,btnY)
        btn1.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn1.setToolTip('Click to CONNECT to devices')
        btn1.released.connect(self.re_init)        
        
        nx = 0
        ny = 1
        btn2 = QtGui.QPushButton('Read position', self)
        btn2.resize(btnX,btnY)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Click to get positions')
        btn2.released.connect(self.readPos)
        
        nx = 1
        ny = 2
        btn3 = QtGui.QPushButton('Change SPEED', self)
        btn3.resize(btnX,btnY)
        btn3.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn3.setToolTip('Click to change speed settings')
        btn3.released.connect(self.chgSpeed)
        
        nx = 1
        ny = 0
        btn4 = QtGui.QPushButton('Change ALPHA (VPH AOI)',self)
        btn4.resize(btnX,btnY)
        btn4.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn4.setToolTip('Change incidence angle (VPH grating)')
        btn4.released.connect(self.alpha_deg) 
        
        nx = 1
        ny = 1
        btn5 = QtGui.QPushButton('Change BETA (detector)',self)
        btn5.resize(btnX,btnY)
        btn5.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn5.setToolTip('Change the diffracted angle (detector)')
        btn5.released.connect(self.beta_deg)
        
        nx = 0
        ny = 2
        btn6 = QtGui.QPushButton('Re-HOME',self)
        btn6.resize(btnX,btnY)
        btn6.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn6.setToolTip('Re-home to recalibrate')
        btn6.released.connect(self.goHome)
        
        return
        
    def re_init(self):
        global hit
        try:
            hit
        except NameError:
            hit = sigko.init_hit()
        else:
            sigko.closeSG(hit)
            hit = sigko.init_hit()

    def readPos(self):
        print "current SigKo positions..."
        mainGUI.update_display(sigma=True)
        print "---"
        
    def chgSpeed(self):
        global hit
        items = ("1: slow (default)","2: medium","3: fast")
        units = {items[0]:1,items[1]:2,items[2]:3}
        item, okPressed = QtGui.QInputDialog.getItem(self, "OptoSigma speed","Select speed (default = 2):", items, 0, False)
        spdVal = units[str(item)]
        if okPressed:
            mainGUI.statusBar().showMessage('Unit selected: '+str(item),5000)
            sigko.speed(hit,spdVal)
#                self.update_display(sigm=True)
        print "---"
        
    def alpha_deg(self):
        global hit
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter new alpha angle')
        if ok:
#            print "Go to (alpha): "+str(text)+" deg"
            mainGUI.statusBar().showMessage('Moving grating to '+str(text)+' deg',5000)
            deg = np.double(text)
            stat = kauto.alpha_move(deg)
#            stat = True
            if stat == 1:
                mainGUI.update_display(sigma=True)
                print "COMPLETE ---"
            else:
                print "ABORT!"
        return
    
    def beta_deg(self):
        global hit
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter new beta angle')
        if ok:
#            print "Go to (beta): "+str(text)+" deg"
            mainGUI.statusBar().showMessage('Moving grating to '+str(text)+' deg',5000)
            deg = np.double(text)   
            stat = kauto.beta_move(deg)
#            stat = True            
            if stat == 1:
                mainGUI.update_display(sigma=True)
                print "COMPLETE ---"
            else:
                print "ABORT!"
                
    def goHome(self):
        global hit
        mainGUI.statusBar().showMessage('Re-homing stages',5000)
        kauto.reHome(sigma=True)
        mainGUI.update_display(sigma=True)
        print "COMPLETE ---"
        return

class velmex_Window(QtGui.QWidget):
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global mainGUI,osGUI,vxGUI,pmGUI
    global vxm,hit,npm,jyh
    global stgCent
    
    
    def __init__(self):
        xsize=450
        ysize=300
        global xcnst
        global ycnst
        xcnst=1.5
        ycnst=0.5
        super(velmex_Window,self).__init__()
        self.setWindowTitle("Velmex controls") 
        self.setGeometry(300,50,xsize,ysize)
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        self.vxButtons()
        
    def vxButtons(self):
        nx = 0
        ny = 0
        btn1 = QtGui.QPushButton('Reconnect', self)
        btn1.setStyleSheet("background-color:purple;border")
        btn1.resize(btnX,btnY)
        btn1.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn1.setToolTip('Click to CONNECT to devices')
        btn1.released.connect(self.re_init)        
        
        nx = 0
        ny = 1
        btn2 = QtGui.QPushButton('Read position', self)
        btn2.resize(btnX,btnY)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Click to get positions')
        btn2.released.connect(self.readPos)
        
        nx = 0
        ny = 2
        btn3 = QtGui.QPushButton('Re-HOME',self)
        btn3.resize(btnX,btnY)
        btn3.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn3.setToolTip('Re-home to recalibrate')
        btn3.released.connect(self.goHome)
        
        nx = 1
        ny = 0
        btn4 = QtGui.QPushButton('Change X (Grating)',self)
        btn4.resize(btnX,btnY)
        btn4.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn4.setToolTip('Change grating translation')
        btn4.released.connect(self.vxm_x) 
        
        nx = 1
        ny = 1
        btn5 = QtGui.QPushButton('Change Y1 (Detector)',self)
        btn5.resize(btnX,btnY)
        btn5.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn5.setToolTip('Change source vertical')
        btn5.released.connect(self.vxm_y1)
        
        nx = 1
        ny = 2
        btn6 = QtGui.QPushButton('Change Y2 (Source)',self)
        btn6.resize(btnX,btnY)
        btn6.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn6.setToolTip('Detector source vertical')
        btn6.released.connect(self.vxm_y2)
        
        return
        
    def re_init(self):
        global hit
        print "HI:"
        
    def readPos(self):
        print "current Velmex positions..."
        mainGUI.update_display(linstage=True)
        print "---"
        
    def goHome(self):
        global hit
        mainGUI.statusBar().showMessage('Re-homing stages',5000)
        kauto.reHome(velmex=True)
        mainGUI.update_display(linstage=True)
        print "COMPLETE ---"
        return
    def vxm_x(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter new position (from center)')
        if ok:
            xmove=np.double(text)
            kauto.horiz_move(xmove)
            mainGUI.update_display(linstage=True)
        return
    def vxm_y1(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter new position (from center)')
        if ok:
            vmove=np.double(text)
            kauto.vert_move(vmove,detector=True)
            mainGUI.update_display(linstage=True)
        return
    def vxm_y2(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter new position (from center)')
        if ok:
            vmove=np.double(text)
            kauto.vert_move(vmove,source=True)
            mainGUI.update_display(linstage=True)
        return
   
class JYmono_Window(QtGui.QWidget):
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global mainGUI,osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI
    global vxm,hit,npm,jyh
    
    def __init__(self):
        xsize=450
        ysize=200
        global xcnst
        global ycnst
        xcnst=1.5
        ycnst=0.5
        super(JYmono_Window,self).__init__()
        self.setWindowTitle("JYHoriba controls") 
        self.setGeometry(300,50,xsize,ysize)
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        self.jyButtons()
    def jyButtons(self):
        nx = 0
        ny = 0
        btn1 = QtGui.QPushButton('Reconnect', self)
        btn1.setStyleSheet("background-color:purple;border")
        btn1.resize(btnX,btnY)
        btn1.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn1.setToolTip('Click to CONNECT to devices')

        nx = 0
        ny = 1
        btn2 = QtGui.QPushButton('Change offset value', self)
        btn2.resize(btnX,btnY)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Change the home offset')
        btn2.released.connect(self.newOffset)
        
    def newOffset(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog','Enter new home-offset')
        if ok:
            print "Mono: new offset = "+str(text)
            reply = QtGui.QMessageBox.question(self, 'Prompt', 'Send monochromator to home?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                mainGUI.statusBar().showMessage('Moving to new home (TEST)',5000)
                
            else:
                mainGUI.statusBar().showMessage('Make sure to home later...',5000)
# **********************************************************************************************************************************
#   Programming the automation
# **********************************************************************************************************************************
class aoi_Window(QtGui.QWidget):
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global mainGUI,osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI
    global vxm,hit,npm,jyh
    global aoi_ScanParam
    global greenVPH,redVPH
    
    def __init__(self):
        xsize=350
        ysize=350
        global xcnst
        global ycnst
        global e1,e2,e3,e4,e5,e6,e7,e8
        xcnst=1.5
        ycnst=0.5
        super(aoi_Window,self).__init__()
        self.setWindowTitle("Scan settings: Best AOI test") 
        self.setGeometry(300,50,xsize,ysize)
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        elo = QtGui.QFormLayout()        
        
        e1 = QtGui.QLineEdit()
        e1.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        e1.setFont(QtGui.QFont("Arial",14))
        e1.setAlignment(QtCore.Qt.AlignRight)
        e1.setText(str(greenVPH[1][0]))
        elo.addRow("Start wavelength [nm]",e1)  
        
        e2 = QtGui.QLineEdit()
        e2.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        e2.setFont(QtGui.QFont("Arial",14))
        e2.setAlignment(QtCore.Qt.AlignRight)
        e2.setText(str(greenVPH[1][1]))
        elo.addRow("End wavelength [nm]",e2)
        
        e3 = QtGui.QLineEdit()
        e3.setValidator(QtGui.QDoubleValidator(-0.99,99.99,2))
        e3.setFont(QtGui.QFont("Arial",14))
        e3.setAlignment(QtCore.Qt.AlignRight)
        e3.setText(str(greenVPH[2]))
        elo.addRow("Wavelength step [nm]",e3)
        
        e4 = QtGui.QLineEdit()
        e4.setValidator(QtGui.QDoubleValidator(-99.99,99.99,2))
        e4.setFont(QtGui.QFont("Arial",14))
        e4.setAlignment(QtCore.Qt.AlignRight)        
        e4.setText(str(greenVPH[3][0]))
        elo.addRow("Start AOI [deg]",e4)
        
        e5 = QtGui.QLineEdit()
        e5.setValidator(QtGui.QDoubleValidator(-99.99,99.99,2))
        e5.setFont(QtGui.QFont("Arial",14))
        e5.setAlignment(QtCore.Qt.AlignRight)
        e5.setText(str(greenVPH[3][1]))
        elo.addRow("End AOI [deg]",e5)
        
        e6 = QtGui.QLineEdit()
        e6.setValidator(QtGui.QDoubleValidator(-99.99,99.99,2))
        e6.setFont(QtGui.QFont("Arial",14))
        e6.setAlignment(QtCore.Qt.AlignRight)
        e6.setText(str(greenVPH[4]))
        elo.addRow("Degree steps [deg]",e6)
        
        e8 = QtGui.QLineEdit()
        e8.setValidator(QtGui.QDoubleValidator(-99.99,99.99,2))
        e8.setFont(QtGui.QFont("Arial",14))
        e8.setAlignment(QtCore.Qt.AlignRight)
        e8.setText(str(greenVPH[0]))
        elo.addRow("Line density [lines/mm]",e8)
        
        e7 = QtGui.QLineEdit()
        e7.setFont(QtGui.QFont("Arial",9))
        e7.setAlignment(QtCore.Qt.AlignRight)
        e7.setText(str(greenVPH[5]+'AOI_'))
        elo.addRow("Filename [.txt]",e7)
        
        self.setLayout(elo)
        self.aoi_buttons()
    
    def aoi_buttons(self):
        nx = 0
        ny = 4.5
        btn1 = QtGui.QRadioButton('&Green VPH', self)
        btn1.resize(btnX/2,btnY/2)
        btn1.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn1.toggled.connect(self.VPHgreen)      
        
        nx = 0.5
        ny = 4.5
        btn3 = QtGui.QRadioButton('&Red VPH', self)
        btn3.resize(btnX/2,btnY/2)
        btn3.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn3.toggled.connect(self.VPHred)    
        
        nx = 1
        ny = 4.5
        btn2 = QtGui.QPushButton('Start scan', self)
        btn2.resize(btnX/2,btnY/2)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Click to start scan')
        btn2.released.connect(self.aoiGO)
        return    
    
    def VPHgreen(self,checked):
        global e1,e2,e3,e4,e5,e6,e7,e8
        global greenVPH
        if checked:
            e1.setText(str(greenVPH[1][0]))
            e2.setText(str(greenVPH[1][1]))
            e3.setText(str(greenVPH[2]))
            e4.setText(str(greenVPH[3][0]))
            e5.setText(str(greenVPH[3][1]))
            e6.setText(str(greenVPH[4]))
            e7.setText(str(greenVPH[5]+'AOI_'))
            e8.setText(str(greenVPH[0]))
            print 'Green VPH selected'
        return        
    def VPHred(self,checked):
        global e1,e2,e3,e4,e5,e6,e7,e8
        global redVPH
        if checked:
            e1.setText(str(redVPH[1][0]))
            e2.setText(str(redVPH[1][1]))
            e3.setText(str(redVPH[2]))
            e4.setText(str(redVPH[3][0]))
            e5.setText(str(redVPH[3][1]))
            e6.setText(str(redVPH[4]))
            e7.setText(str(redVPH[5]+'AOI_'))
            e8.setText(str(redVPH[0]))
            print 'Red VPH selected'
        return    
    
    def confirmAction(self):
        global e1,e2,e3,e4,e5,e6,e7,e8
        global mainGUI
        global aoi_ScanParam
        wv_start    = np.int(e1.text())
        wv_end      = np.int(e2.text())
        wv_step     = np.int(e3.text())
        wavelength  = [wv_start,wv_end,wv_step]
        aoi_start   = np.double(e4.text())
        aoi_end     = np.double(e5.text())
        aoi_step    = np.double(e6.text())
        lineDensity = np.int(e8.text())
        aoi = [aoi_start,aoi_end,aoi_step]
        fileName = str(e7.text())
        stp = str.split(fileName,'.txt')
        if len(stp) == 1:
            fileName += '.txt'
        aoi_ScanParam = [wavelength,aoi,fileName,lineDensity]        
        mainGUI.statusBar().showMessage('Best AOI test parameters saved',5000)
        return
    def check_values(self,scan_parameters):
        redFLAG = False
        wv_start = scan_parameters[0][0]
        wv_end   = scan_parameters[0][1]
        wv_step  = scan_parameters[0][2]
        if wv_start < 0 or wv_end < 0:
            print "ERROR: check wavelength signs"
            redFLAG = True
        if np.fabs(np.fabs(wv_end) - np.fabs(wv_start))!=0 and np.fabs(np.fabs(wv_end) - np.fabs(wv_start)) < np.fabs(wv_step):
            print "ERROR: check wavelength inputs"
            redFLAG = True
        aoi_start = scan_parameters[1][0]
        aoi_end   = scan_parameters[1][1]
        aoi_step  = scan_parameters[1][2]
        if  np.fabs(np.fabs(aoi_end) - np.fabs(aoi_start)) != 0 and np.fabs(np.fabs(aoi_end) - np.fabs(aoi_start)) < np.fabs(aoi_step):
            print "ERROR: check AOI inputs"
            redFLAG = True
        if np.fabs(aoi_step) >= 3:
            print "ERROR: check AOI step size"
            redFLAG = True
        return redFLAG
        
    def aoiGO(self):
        global mainGUI
        global aoi_ScanParam,saveDir
        self.confirmAction()
        redFLAG = self.check_values(aoi_ScanParam)
        if redFLAG == True:
            print "ABORT!"
            return
        wavelen     = aoi_ScanParam[0]
        aoi         = aoi_ScanParam[1]
        filename    = aoi_ScanParam[2]
        lineDensity = aoi_ScanParam[3]
        saveFile = filename
        fileStatus = kauto.check_dataFile(saveDir,filename)
        if fileStatus == True:
            reply = QtGui.QMessageBox.question(self, 'Warning: check filename', 
                             saveFile+' already exists. Do you want to overwrite?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                print 'Overwriting ',saveFile
            else:
                print 'OK change the filename please'
                return
        mainGUI.statusBar().showMessage('Running best AOI test',10000)
        status = kauto.bestAOI_test(wavelen,aoi,lineDensity,saveFile)
        if status == -1:
            print 'ERROR'
            return
        else:
            print '==============================================='
            print '*GUI: AOI SCAN FINISHED'
            print '==============================================='
            return
        
class fullGrating_Window(QtGui.QWidget):
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global mainGUI,osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI
    global vxm,hit,npm,jyh
    global greenVPH,redVPH
    
    def __init__(self):
        xsize=350
        ysize=350
        global xcnst
        global ycnst
        global f1,f2,f3,f4,f5,f6,f7,f8
        xcnst=1.5
        ycnst=0.5
        super(fullGrating_Window,self).__init__()
        self.setWindowTitle("Scan settings: Full grating scan test") 
        self.setGeometry(300,50,xsize,ysize)
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        flo = QtGui.QFormLayout()        
        
        f1 = QtGui.QLineEdit()
        f1.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        f1.setFont(QtGui.QFont("Arial",14))
        f1.setAlignment(QtCore.Qt.AlignRight)
        f1.setText(str(greenVPH[1][0]))
        flo.addRow("Start wavelength [nm]",f1)  
        
        f2 = QtGui.QLineEdit()
        f2.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        f2.setFont(QtGui.QFont("Arial",14))
        f2.setAlignment(QtCore.Qt.AlignRight)
        f2.setText(str(greenVPH[1][1]))
        flo.addRow("End wavelength [nm]",f2)
        
        f3 = QtGui.QLineEdit()
        f3.setValidator(QtGui.QDoubleValidator(-0.99,99.99,2))
        f3.setFont(QtGui.QFont("Arial",14))
        f3.setAlignment(QtCore.Qt.AlignRight)
        f3.setText(str(greenVPH[2]))
        flo.addRow("Wavelength step [nm]",f3)
        
        f4 = QtGui.QLineEdit()
        f4.setValidator(QtGui.QDoubleValidator(-0.99,99.99,2))
        f4.setFont(QtGui.QFont("Arial",14))
        f4.setAlignment(QtCore.Qt.AlignRight)
        flo.addRow("Best AOI [deg]",f4) 
        
        f7 = QtGui.QLineEdit()
        f7.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        f7.setFont(QtGui.QFont("Arial",14))
        f7.setAlignment(QtCore.Qt.AlignRight)
        f7.setText(str(greenVPH[6]))
        flo.addRow("Dist from Center [in]",f7) 
        
        f8 = QtGui.QLineEdit()
        f8.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        f8.setFont(QtGui.QFont("Arial",14))
        f8.setAlignment(QtCore.Qt.AlignRight)
        f8.setText(str(greenVPH[7]))
        flo.addRow("Step size [in]",f8) 
        
        f6 = QtGui.QLineEdit()
        f6.setValidator(QtGui.QDoubleValidator(-0.99,99.99,2))
        f6.setFont(QtGui.QFont("Arial",14))
        f6.setAlignment(QtCore.Qt.AlignRight)
        f6.setText(str(greenVPH[0]))
        flo.addRow("Line density [lines/mm]",f6) 
        
        f5 = QtGui.QLineEdit()
        f5.setFont(QtGui.QFont("Arial",9))
        f5.setAlignment(QtCore.Qt.AlignRight)
        f5.setText(str('fullGrat_'+greenVPH[5]))
        flo.addRow("Filename [.txt]",f5)

        self.setLayout(flo)
        self.fullGrat_buttons()
        
    def fullGrat_buttons(self):
        nx = 0
        ny = 4.5
        btn1 = QtGui.QRadioButton('&Green VPH', self)
        btn1.resize(btnX/2,btnY/2)
        btn1.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn1.toggled.connect(self.VPHgreen)      
        
        nx = 0.5
        ny = 4.5
        btn3 = QtGui.QRadioButton('&Red VPH', self)
        btn3.resize(btnX/2,btnY/2)
        btn3.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn3.toggled.connect(self.VPHred)    
        
        nx = 1
        ny = 4.5
        btn2 = QtGui.QPushButton('Start scan', self)
        btn2.resize(btnX/2,btnY/2)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Click to start scan')
        btn2.released.connect(self.fullGratGO)
        return
    
    def VPHgreen(self,checked):
        global f1,f2,f3,f4,f5,f6,f7,f8
        global greenVPH
        if checked:
            f1.setText(str(greenVPH[1][0]))
            f2.setText(str(greenVPH[1][1]))
            f3.setText(str(greenVPH[2]))
            f6.setText(str(greenVPH[0]))
            f7.setText(str(greenVPH[6]))
            f8.setText(str(greenVPH[7]))
            f5.setText(str('fullGrat_'+greenVPH[5]))
            print 'Green VPH selected'
        return        
    def VPHred(self,checked):
        global f1,f2,f3,f4,f5,f6,f7,f8
        global redVPH
        if checked:
            f1.setText(str(redVPH[1][0]))
            f2.setText(str(redVPH[1][1]))
            f3.setText(str(redVPH[2]))
            f6.setText(str(redVPH[0]))
            f7.setText(str(redVPH[6]))
            f8.setText(str(redVPH[7]))
            f5.setText(str('fullGrat_'+redVPH[5]))
            print 'Red VPH selected'
        return    
        
    def confirmAction(self):
        global f1,f2,f3,f4,f5,f6
        global mainGUI
        global fullGrat_ScanParam
        wv_start   = np.int(f1.text())
        wv_end     = np.int(f2.text())
        wv_step    = np.int(f3.text())
        wavelength = [wv_start,wv_end,wv_step]
        best_AOI   = np.double(f4.text())
        fileName   = str(f5.text())
        lineDensity  = np.int(f6.text())
        distFromCent = np.double(f7.text())
        scanStepSize = np.double(f8.text())
        lineDensity  = np.int(f6.text())
        stp = str.split(fileName,'.txt')
        if len(stp) == 1:
            fileName += '.txt'
        print fileName
        fullGrat_ScanParam = [wavelength,best_AOI,fileName,lineDensity,distFromCent,scanStepSize]
        mainGUI.statusBar().showMessage('Full grating scan parameters saved',5000)
        
        # need to add a check so that the inputs don't kill the program
        return 
    def check_values(self,scan_parameters):
        global VPH_clearAperture
        redFLAG = False
        wv_start = scan_parameters[0][0]
        wv_end   = scan_parameters[0][1]
        wv_step  = scan_parameters[0][2]
        if wv_start < 0 or wv_end < 0:
            print "ERROR: check wavelength signs"
            redFLAG = True
        if np.fabs(np.fabs(wv_end) - np.fabs(wv_start))!=0 and np.fabs(np.fabs(wv_end) - np.fabs(wv_start)) < np.fabs(wv_step):
            print "ERROR: check wavelength inputs"
            redFLAG = True
        distFromCent = scan_parameters[4]
        scanStepSize  = scan_parameters[5]
        if distFromCent > VPH_clearAperture:
            print "ERROR: scan range too large"
            redFLAG = True
        if scanStepSize > distFromCent:
            print "ERROR: scan step is too big"
            redFLAG = True
        return redFLAG
        
        
    def fullGratGO(self):
        global mainGUI,fullGrat_ScanParam
        self.confirmAction()
        wavelen      = fullGrat_ScanParam[0]
        bestAOI      = fullGrat_ScanParam[1]
        filename     = fullGrat_ScanParam[2]
        lineDensity  = fullGrat_ScanParam[3]
        distFromCent = fullGrat_ScanParam[4]
        scanStepSize = fullGrat_ScanParam[5]
        scanParam = [distFromCent,scanStepSize]
        redFLAG = self.check_values(fullGrat_ScanParam)
        if redFLAG == True:
            print "ABORT!"
            return
        saveFile = filename
        fileStatus = kauto.check_dataFile(saveDir,filename)
        if fileStatus == True:
            reply = QtGui.QMessageBox.question(self, 'Warning: check filename', 
                             saveFile+' already exists. Do you want to overwrite?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                print 'Overwriting ',saveFile
            else:
                print 'OK change the filename please'
                return
        print 'Full grating scan: start!'
        mainGUI.statusBar().showMessage('Running Full grating scan',10000)
        status = kauto.fullGrating_sweep2(wavelen,bestAOI,lineDensity,scanParam,saveFile,HORIZ=True,VERT=True,DIAG=True)
        if status == -1:
            print 'ERROR'
            return
        else:
            print '==============================================='
            print '*GUI: FULL GRATING SCAN FINISHED'
            print '==============================================='
            return

class customScan_Window(QtGui.QWidget):
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global mainGUI,osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI
    global vxm,hit,npm,jyh
    global greenVPH,redVPH
    
    def __init__(self):
        xsize=350
        ysize=450
        global xcnst
        global ycnst
        global c1,c2,c3,c4,c5,c6,c7,c8
        xcnst=1.5
        ycnst=0.5
        super(customScan_Window,self).__init__()
        self.setWindowTitle("Scan settings: Custom scan test") 
        self.setGeometry(300,50,xsize,ysize)
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        clo = QtGui.QFormLayout()        
        
        c1 = QtGui.QLineEdit()
        c1.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        c1.setFont(QtGui.QFont("Arial",14))
        c1.setAlignment(QtCore.Qt.AlignRight)
        c1.setText(str(greenVPH[1][0]))
        clo.addRow("Start wavelength [nm]",c1)  
        
        c2 = QtGui.QLineEdit()
        c2.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        c2.setFont(QtGui.QFont("Arial",14))
        c2.setAlignment(QtCore.Qt.AlignRight)
        c2.setText(str(greenVPH[1][1]))
        clo.addRow("End wavelength [nm]",c2)
        
        c3 = QtGui.QLineEdit()
        c3.setValidator(QtGui.QDoubleValidator(-0.99,99.99,2))
        c3.setFont(QtGui.QFont("Arial",14))
        c3.setAlignment(QtCore.Qt.AlignRight)
        c3.setText(str(greenVPH[2]))
        clo.addRow("Wavelength step [nm]",c3)
        
        c4 = QtGui.QLineEdit()
        c4.setValidator(QtGui.QDoubleValidator(-0.99,99.99,2))
        c4.setFont(QtGui.QFont("Arial",14))
        c4.setAlignment(QtCore.Qt.AlignRight)
        clo.addRow("Best AOI [deg]",c4) 
        
        c7 = QtGui.QLineEdit()
        c7.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        c7.setFont(QtGui.QFont("Arial",14))
        c7.setAlignment(QtCore.Qt.AlignRight)
        c7.setText(str(greenVPH[6]))
        clo.addRow("Dist from Center [in]",c7) 
        
        c8 = QtGui.QLineEdit()
        c8.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        c8.setFont(QtGui.QFont("Arial",14))
        c8.setAlignment(QtCore.Qt.AlignRight)
        c8.setText(str(greenVPH[7]))
        clo.addRow("Step size [in]",c8) 
        
        c6 = QtGui.QLineEdit()
        c6.setValidator(QtGui.QDoubleValidator(-0.99,99.99,2))
        c6.setFont(QtGui.QFont("Arial",14))
        c6.setAlignment(QtCore.Qt.AlignRight)
        c6.setText(str(greenVPH[0]))
        clo.addRow("Line density [lines/mm]",c6) 
        
        c5 = QtGui.QLineEdit()
        c5.setFont(QtGui.QFont("Arial",9))
        c5.setAlignment(QtCore.Qt.AlignRight)
        c5.setText(str('fullGrat_'+greenVPH[5]))
        clo.addRow("Filename [.txt]",c5)

        self.setLayout(clo)
        self.fullGrat_buttons()
        
    def fullGrat_buttons(self):
        nx = 0
        ny = 4.5
        btn1 = QtGui.QRadioButton('&Green VPH', self)
        btn1.resize(btnX/2,btnY/2)
        btn1.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn1.toggled.connect(self.VPHgreen)      
        
        nx = 0.5
        ny = 4.5
        btn3 = QtGui.QRadioButton('&Red VPH', self)
        btn3.resize(btnX/2,btnY/2)
        btn3.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn3.toggled.connect(self.VPHred)    
        
        nx = 1
        ny = 4.5
        btn2 = QtGui.QPushButton('Horiz. scan', self)
        btn2.resize(btnX/2,btnY/2)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Click to start scan')
        btn2.released.connect(self.horizGratGO)
        
        nx = 1
        ny = 5
        btn2 = QtGui.QPushButton('Vert. scan', self)
        btn2.resize(btnX/2,btnY/2)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Click to start scan')
        btn2.released.connect(self.vertGratGO)

        nx = 1
        ny = 5.5
        btn2 = QtGui.QPushButton('Diag. scan', self)
        btn2.resize(btnX/2,btnY/2)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.setToolTip('Click to start scan')
        btn2.released.connect(self.diagGratGO)
        
        return
    
    def VPHgreen(self,checked):
        global c1,c2,c3,c4,c5,c6,c7,c8
        global greenVPH
        if checked:
            c1.setText(str(greenVPH[1][0]))
            c2.setText(str(greenVPH[1][1]))
            c3.setText(str(greenVPH[2]))
            c6.setText(str(greenVPH[0]))
            c7.setText(str(greenVPH[6]))
            c8.setText(str(greenVPH[7]))
            c5.setText(str('fullGrat_'+greenVPH[5]))
            print 'Green VPH selected'
        return        
    def VPHred(self,checked):
        global c1,c2,c3,c4,c5,c6,c7,c8
        global redVPH
        if checked:
            c1.setText(str(redVPH[1][0]))
            c2.setText(str(redVPH[1][1]))
            c3.setText(str(redVPH[2]))
            c6.setText(str(redVPH[0]))
            c7.setText(str(redVPH[6]))
            c8.setText(str(redVPH[7]))
            c5.setText(str('fullGrat_'+redVPH[5]))
            print 'Red VPH selected'
        return    
        
    def confirmAction(self):
        global c1,c2,f3,c4,c5,c6
        global mainGUI
        global custom_ScanParam
        wv_start   = np.int(c1.text())
        wv_end     = np.int(c2.text())
        wv_step    = np.int(c3.text())
        wavelength = [wv_start,wv_end,wv_step]
        best_AOI   = np.double(c4.text())
        fileName   = str(c5.text())
        lineDensity  = np.int(c6.text())
        distFromCent = np.double(c7.text())
        scanStepSize = np.double(c8.text())
        lineDensity  = np.int(c6.text())
        stp = str.split(fileName,'.txt')
        if len(stp) == 1:
            fileName += '.txt'
        custom_ScanParam = [wavelength,best_AOI,fileName,lineDensity,distFromCent,scanStepSize]
        mainGUI.statusBar().showMessage('Full grating scan parameters saved',5000)
        
        # need to add a check so that the inputs don't kill the program
        return 
    def check_values(self,scan_parameters):
        global VPH_clearAperture
        redFLAG = False
        wv_start = scan_parameters[0][0]
        wv_end   = scan_parameters[0][1]
        wv_step  = scan_parameters[0][2]
        if wv_start < 0 or wv_end < 0:
            print "ERROR: check wavelength signs"
            redFLAG = True
        if np.fabs(np.fabs(wv_end) - np.fabs(wv_start))!=0 and np.fabs(np.fabs(wv_end) - np.fabs(wv_start)) < np.fabs(wv_step):
            print "ERROR: check wavelength inputs"
            redFLAG = True
        distFromCent = scan_parameters[4]
        scanStepSize  = scan_parameters[5]
        if distFromCent > VPH_clearAperture:
            print "ERROR: scan range too large"
            redFLAG = True
        if scanStepSize > distFromCent:
            print "ERROR: scan step is too big"
            redFLAG = True
        return redFLAG

    def horizGratGO(self):
        self.customGO(1)
        return
    def vertGratGO(self):
        self.customGO(2)
        return
    def diagGratGO(self):
        self.customGO(3)
        return
    
    def customGO(self,scanID):
        global mainGUI,custom_ScanParam
        self.confirmAction()
        wavelen      = custom_ScanParam[0]
        bestAOI      = custom_ScanParam[1]
        filename     = custom_ScanParam[2]
        lineDensity  = custom_ScanParam[3]
        distFromCent = custom_ScanParam[4]
        scanStepSize = custom_ScanParam[5]
        scanParam = [distFromCent,scanStepSize]
        redFLAG = self.check_values(custom_ScanParam)
        if redFLAG == True:
            print "ABORT!"
            return
        saveFile = filename
        fileStatus = kauto.check_dataFile(saveDir,filename)
        if fileStatus == True:
            reply = QtGui.QMessageBox.question(self, 'Warning: check filename', 
                             saveFile+' already exists. Do you want to overwrite?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                print 'Overwriting ',saveFile
            else:
                print 'OK change the filename please'
                return
        print 'Full grating scan: start!'
        status = -1
        if scanID == 1:
            status = kauto.fullGrating_sweep2(wavelen,bestAOI,lineDensity,scanParam,saveFile,HORIZ=True)
        if scanID == 2:
            status = kauto.fullGrating_sweep2(wavelen,bestAOI,lineDensity,scanParam,saveFile,VERT=True)
        if scanID == 3:
            status = kauto.fullGrating_sweep2(wavelen,bestAOI,lineDensity,scanParam,saveFile,DIAG=True)
        if status == -1:
            print 'ERROR'
            return
        else:
            print '==============================================='
            print '*GUI: CUSTOM SCAN '+str(scanID)+' FINISHED'
            print '==============================================='
            return

class waveScan_Window(QtGui.QWidget):
    global btnSpace,btnX,btnY,menuSize,frameSpace
    global mainGUI,osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI
    global vxm,hit,npm,jyh
    global greenVPH,redVPH
    
    def __init__(self):
        xsize=350
        ysize=300
        global xcnst
        global ycnst
        global w1,w2,w3,w4,w5,w6
        
        xcnst=1.5
        ycnst=0.5
        super(waveScan_Window,self).__init__()
        self.setWindowTitle("Scan settings: Wavelength scan test") 
        self.setGeometry(300,50,xsize,ysize)
        self.setWindowIcon(QtGui.QIcon('kpf_logo.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Plastique"))
        wlo = QtGui.QFormLayout()        
        
        w1 = QtGui.QLineEdit()
        w1.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        w1.setFont(QtGui.QFont("Arial",14))
        w1.setAlignment(QtCore.Qt.AlignRight)
        w1.setText(str(greenVPH[1][0]))
        wlo.addRow("Start wavelength [nm]",w1)  
        
        w2 = QtGui.QLineEdit()
        w2.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        w2.setFont(QtGui.QFont("Arial",14))
        w2.setAlignment(QtCore.Qt.AlignRight)
        w2.setText(str(greenVPH[1][1]))
        wlo.addRow("End wavelength [nm]",w2)
        
        w3 = QtGui.QLineEdit()
        w3.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        w3.setFont(QtGui.QFont("Arial",14))
        w3.setAlignment(QtCore.Qt.AlignRight)
        w3.setText(str(greenVPH[2]))
        wlo.addRow("Wavelength step [nm]",w3)
        
        w4 = QtGui.QLineEdit()
        w4.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        w4.setFont(QtGui.QFont("Arial",14))
        w4.setAlignment(QtCore.Qt.AlignRight)
        w4.setText(str(5))
        wlo.addRow("Integration time [s]",w4)
        
        w6 = QtGui.QLineEdit()
        w6.setValidator(QtGui.QDoubleValidator(0.99,99.99,2))
        w6.setFont(QtGui.QFont("Arial",14))
        w6.setAlignment(QtCore.Qt.AlignRight)
        w6.setText(str(greenVPH[0]))
        wlo.addRow("Line density [lines/mm]",w6)
        
        w5 = QtGui.QLineEdit()
        w5.setFont(QtGui.QFont("Arial",9))
        w5.setAlignment(QtCore.Qt.AlignRight)
        w5.setText(str(greenVPH[5]+'waveScan_'))
        wlo.addRow("Filename [.txt]",w5)

        self.setLayout(wlo)
        self.wave_buttons()
        
    def wave_buttons(self):
        nx = 0
        ny = 3.0
        btn1 = QtGui.QRadioButton('&w/Green VPH', self)
        btn1.resize(btnX/2,btnY/2)
        btn1.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn1.toggled.connect(self.VPHgreen)  
        
        nx = 0
        ny = 3.3
        btn2 = QtGui.QRadioButton('&w/Red VPH', self)
        btn2.resize(btnX/2,btnY/2)
        btn2.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn2.toggled.connect(self.VPHred)
        
        nx = 0.5
        ny = 3.0
        btn3 = QtGui.QRadioButton('&No diffraction', self)
        btn3.resize(btnX/2,btnY/2)
        btn3.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn3.toggled.connect(self.woGrating)
        
        nx = 1.0
        ny = 3.0
        btn4 = QtGui.QPushButton('Start scan', self)
        btn4.resize(btnX/2,btnY/2)
        btn4.move(frameSpace+btnX*nx+btnSpace*nx,frameSpace+btnY*ny+menuSize+btnSpace*ny)
        btn4.setToolTip('Click to start scan')
        btn4.released.connect(self.waveScanGO)
        return
        
    def VPHgreen(self,checked):
        global w1,w2,w3,w4,w5,w6
        global greenVPH
        global noGrating
        if checked:
            noGrating = False
            print 'w/Green Grating --> will find diffraction'
            w1.setText(str(greenVPH[1][0]))
            w2.setText(str(greenVPH[1][1]))
            w3.setText(str(greenVPH[2]))
            w6.setText(str(greenVPH[0]))
            w5.setText(str(greenVPH[5]+'waveScan_'))
        return
    def VPHred(self,checked):
        global w1,w2,w3,w4,w5,w6
        global redVPH
        global noGrating
        if checked:
            noGrating = False
            w1.setText(str(redVPH[1][0]))
            w2.setText(str(redVPH[1][1]))
            w3.setText(str(redVPH[2]))
            w6.setText(str(redVPH[0]))
            w5.setText(str(redVPH[5]+'waveScan_'))
            print 'w/Red Grating --> will find diffraction'
        return 
    def woGrating(self,checked):
        global w1,w2,w3,w4,w5,w6
        global noGrating
        if checked:
            noGrating = True
            w6.setText(str(0))
            w5.setText(str('waveScan_'))
            print 'w/o Grating --> detector will not rotate'
        return    
    
        
    def confirmAction(self):
        global w1,w2,w3,w4,w5
        global mainGUI,wvGUI
        global waveScan_param
        
        wv_start   = np.int(w1.text())
        wv_end     = np.int(w2.text())
        wv_step    = np.int(w3.text())
        itime      = np.int(w4.text())
        lineDensity = np.int(w6.text())
        wavelength = [wv_start,wv_end,wv_step]
        fileName = str(w5.text())
        stp = str.split(fileName,'.txt')
        if len(stp) == 1:
            fileName += '.txt'
        waveScan_param = [wavelength,fileName,itime,lineDensity]
        mainGUI.statusBar().showMessage('Full grating scan parameters saved',5000)
        return
        
    def waveScanGO(self):
        global mainGUI
        global waveScan_param,saveDir
        global np3,npm,JYhoriba,jyh
        global noGrating
        
        self.confirmAction()
        filename = waveScan_param[1]        
        wavelen = waveScan_param[0]
        itime = waveScan_param[2]
        lineDensity = waveScan_param[3]
        saveFile = filename
        fileStatus = kauto.check_dataFile(saveDir,filename)
        if fileStatus == True:
            reply = QtGui.QMessageBox.question(self, 'Warning: check filename', 
                             saveFile+' already exists. Do you want to overwrite?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                print 'Overwriting ',saveFile
            else:
                print 'OK change the filename please'
                return
        
        mainGUI.statusBar().showMessage('Running wavelength scan',10000)    
        curSig = kauto.sigko_positions()
        alpha = curSig[0][1]
        beta  = curSig[0][0]
        vxm1i,vxm1  = kauto.vxm_positions(dev=1)
        vxm2i,vxm2  = kauto.vxm_positions(dev=2)
        vxm3i,vxm3  = kauto.vxm_positions(dev=3)        
        status = kauto.waveScan(wavelen,itime,saveFile,GRATSWEEP=[alpha,beta,vxm1i,vxm2i,vxm3i],FIXEDPOS=noGrating,lineDensity=lineDensity)
        if status == -1:
            print 'ERROR'
            return
        else:
            print '==============================================='
            print '*GUI: WAVELENGTH SCAN FINISHED'
            print '==============================================='
            return

# **********************************************************************************************************************************
# Run the main GUI program
# ********************************************************************************************************************************** 
def run_GUI():
    global mainGUI
    global osGUI,vxGUI,pmGUI,jyGUI,a0GUI,fgGUI,wvGUI,cmGUI
    
    if __name__ == '__main__':
        app = QtGui.QApplication(sys.argv)
        mainGUI = KPF_VPH_GUI()
        osGUI = optSg_Window()
        jyGUI = JYmono_Window()  
        vxGUI = velmex_Window()
        a0GUI = aoi_Window()
        fgGUI = fullGrating_Window()
        wvGUI = waveScan_Window()
        cmGUI = customScan_Window()
        
        mainGUI.show()
        sys.exit(app.exec_())

run_GUI()