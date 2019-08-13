from tkinter import *
import serial
import time
import os

x = [0,200,400,600,800,1000,1200,1400,1600]
y = [0,150,300,450,600]
width = 10
serial_port = 'COM5'

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master = master
        self.init_window()

    
    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget      
        self.master.title("GUI")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating and placing a button instance
        Button_A1 = Button(self, text="A1", width = width, height = 2,command=ButtonA1)
        Button_A1.place(x=x[0], y=y[0])

        Button_A2 = Button(self, text="A2", width = width, height = 2,command=ButtonA2)
        Button_A2.place(x=x[0], y=y[1])

        Button_A3 = Button(self, text="A3", width = width, height = 2,command=ButtonA3)
        Button_A3.place(x=x[0], y=y[2])

        Button_A4 = Button(self, text="A4", width = width, height = 2,command=ButtonA4)
        Button_A4.place(x=x[0], y=y[3])

        Button_A5 = Button(self, text="A5", width = width, height = 2,command=ButtonA5)
        Button_A5.place(x=x[0], y=y[4])

        # creating and placing a button instance
        Button_B1 = Button(self, text="B1", width = width, height = 2,command=ButtonB1)
        Button_B1.place(x=x[1], y=y[0])

        Button_B2 = Button(self, text="B2", width = width, height = 2,command=ButtonB2)
        Button_B2.place(x=x[1], y=y[1])

        Button_B3 = Button(self, text="B3", width = width, height = 2,command=ButtonB3)
        Button_B3.place(x=x[1], y=y[2])

        Button_B4 = Button(self, text="B4", width = width, height = 2,command=ButtonB4)
        Button_B4.place(x=x[1], y=y[3])

        Button_B5 = Button(self, text="B5", width = width, height = 2,command=ButtonB5)
        Button_B5.place(x=x[1], y=y[4])

                # creating and placing a button instance
        Button_C1 = Button(self, text="C1", width = width, height = 2,command=ButtonC1)
        Button_C1.place(x=x[2], y=y[0])

        Button_C2 = Button(self, text="C2", width =width, height = 2,command=ButtonC2)
        Button_C2.place(x=x[2], y=y[1])

        Button_C3 = Button(self, text="C3", width = width, height = 2,command=ButtonC3)
        Button_C3.place(x=x[2], y=y[2])

        Button_C4 = Button(self, text="C4", width = width, height = 2,command=ButtonC4)
        Button_C4.place(x=x[2], y=y[3])

        Button_C5 = Button(self, text="C5", width = width, height = 2,command=ButtonC5)
        Button_C5.place(x=x[2], y=y[4])

                # creating and placing a button instance
        Button_D1 = Button(self, text="D1", width = width, height = 2,command=ButtonD1)
        Button_D1.place(x=x[3], y=y[0])

        Button_D2 = Button(self, text="D2", width = width, height = 2,command=ButtonD2)
        Button_D2.place(x=x[3], y=y[1])

        Button_D3 = Button(self, text="D3", width = width, height = 2,command=ButtonD3)
        Button_D3.place(x=x[3], y=y[2])

        Button_D4 = Button(self, text="D4", width = width, height = 2,command=ButtonD4)
        Button_D4.place(x=x[3], y=y[3])

        Button_D5 = Button(self, text="D5", width = width, height = 2,command=ButtonD5)
        Button_D5.place(x=x[3], y=y[4])

                # creating and placing a button instance
        Button_E1 = Button(self, text="E1", width = width, height = 2,command=ButtonE1)
        Button_E1.place(x=x[4], y=y[0])

        Button_E2 = Button(self, text="E2", width = width, height = 2,command=ButtonE2)
        Button_E2.place(x=x[4], y=y[1])

        Button_E3 = Button(self, text="E3", width = width, height = 2,command=ButtonE3)
        Button_E3.place(x=x[4], y=y[2])

        Button_E4 = Button(self, text="E4", width = width, height = 2,command=ButtonE4)
        Button_E4.place(x=x[4], y=y[3])
        
        Button_E5 = Button(self, text="E5", width = width, height = 2,command=ButtonE5)
        Button_E5.place(x=x[4], y=y[4])

        #Fire Buttons
        Button_WindUp_On = Button(self, text="WINDUP_ON", width = width, height = 2,command=Button_WindUpOn)
        Button_WindUp_On.place(x=x[5], y=y[0])
        
        Button_Fire_On = Button(self, text="FIRE_ON", width = width, height = 2,command=Button_FireOn)
        Button_Fire_On.place(x=x[5], y=y[1])
        
        Button_WindUp_Off = Button(self, text="WINDUP_OFF", width = width, height = 2,command=Button_WindUpOff)
        Button_WindUp_Off.place(x=x[5], y=y[2])
        
        Button_Fire_Off = Button(self, text="FIRE_OFF", width = width, height = 2,command=Button_FireOff)
        Button_Fire_Off.place(x=x[5], y=y[3])
        
        Button_HomeButton = Button(self, text="Home", width = width, height = 2,command=Home)
        Button_HomeButton.place(x=x[5], y=y[3])
        
        #Manual Control Buttons
        Button_Up = Button(self, text="Up", width =width, height = 2,command=ButtonUp)
        Button_Up.place(x=x[6], y=y[0])
        
        Button_Down = Button(self, text="Down", width = width, height = 2,command=ButtonDown)
        Button_Down.place(x=x[6], y=y[1])
        
        Button_Left = Button(self, text="Left", width = width, height = 2,command=ButtonLeft)
        Button_Left.place(x=x[6], y=y[2])
        
        Button_Right = Button(self, text="Right", width = width, height = 2,command=ButtonRight)
        Button_Right.place(x=x[6], y=y[3])
        
        #Calibration Buttons
        Button_CalI = Button(self, text="I Cal Set", width = width, height = 2,command=CalISet)
        Button_CalI.place(x=x[7], y=y[0])
        
        Button_CalII = Button(self, text="II Cal Set", width = width, height = 2,command=CalIISet)
        Button_CalII.place(x=x[7], y=y[1])
        
        Button_CalIII = Button(self, text="III Cal Set", width = width, height = 2,command=CalIIISet)
        Button_CalIII.place(x=x[7], y=y[2])   
        
        #Quit
        Button_Quit = Button(self, text="Quit", width = width, height = 2,command=Quit)
        Button_Quit.place(x=x[8], y=y[0])        

        #Play Victory Song!
        Button_VictorySong = Button(self, text="Winning", width = width, height = 2,command=Victory)
        Button_VictorySong.place(x=x[8], y=y[3])        

def ButtonA1():
    print('ButtonA1')
    ser_port.write(b'01')

def ButtonA2():
    print('ButtonA2')
    ser_port.write(b'02')

def ButtonA3():
    print('ButtonA3')
    ser_port.write(b'03')

def ButtonA4():
    print('ButtonA4')
    ser_port.write(b'04')

def ButtonA5():
    print('ButtonA5')
    ser_port.write(b'05')
    
def ButtonB1():
    print('ButtonB1')
    ser_port.write(b'06')

def ButtonB2():
    print('ButtonB2')
    ser_port.write(b'07')

def ButtonB3():
    print('ButtonB3')
    ser_port.write(b'08')

def ButtonB4():
    print('ButtonB4')
    ser_port.write(b'09')

def ButtonB5():
    print('ButtonB5')
    ser_port.write(b'10')
    
def ButtonC1():
    print('ButtonC1')
    ser_port.write(b'11')

def ButtonC2():
    print('ButtonC2')
    ser_port.write(b'12')

def ButtonC3():
    print('ButtonC3')
    ser_port.write(b'13')

def ButtonC4():
    print('ButtonC4')
    ser_port.write(b'14')

def ButtonC5():
    print('ButtonC5')
    ser_port.write(b'15')
    
def ButtonD1():
    print('ButtonD1')
    ser_port.write(b'16')

def ButtonD2():
    print('ButtonD2')
    ser_port.write(b'17')

def ButtonD3():
    print('ButtonD3')
    ser_port.write(b'18')

def ButtonD4():
    print('ButtonD4')
    ser_port.write(b'19')

def ButtonD5():
    print('ButtonD5')
    ser_port.write(b'20')

def ButtonE1():
    print('ButtonE1')
    ser_port.write(b'21')

def ButtonE2():
    print('ButtonE2')
    ser_port.write(b'22')

def ButtonE3():
    print('ButtonE3')
    ser_port.write(b'23')

def ButtonE4():
    print('ButtonE4')
    ser_port.write(b'24')

def ButtonE5():
    print('ButtonE5')
    ser_port.write(b'25')
    
def Button_WindUpOn():
    print('WindUp On')
    ser_port.write(b'26')

def Button_FireOn():
    print('Fire On')
    ser_port.write(b'27')

def Button_WindUpOff():
    print('Windup Off')
    ser_port.write(b'28')

def Button_FireOff():
    print('Fire Off')
    ser_port.write(b'29')
    
def Home():
    print('Home')
    ser_port.write(b'30')
    
def ButtonUp():
    print('Move Up')
    ser_port.write(b'31')

def ButtonDown():
    print('Move Down')
    ser_port.write(b'32')

def ButtonLeft():
    print('Move Left')
    ser_port.write(b'33')

def ButtonRight():
    print('Fire Right')
    ser_port.write(b'34')
    
def CalISet():
    print('First Calibration Set')
    ser_port.write(b'36')

def CalIISet():
    print('Second Calibration Set')
    ser_port.write(b'37')

def CalIIISet():
    print('Third Calibration Set')
    ser_port.write(b'38')
    
def Quit():
    print('Quit')
    ser_port.close()
    root.destroy()
    
def Victory():
    print('Winning')
    file = '"C:\\Users\\Thomas Goehring\\Desktop\\mecha10\\Project_UI\\Adios Turd Nuggets.mp3"'
    os.system(file)

#----------------------------
#Test Code
#----------------------------
    

root = Tk()
#size of the window

root.geometry("2000x1200")
app = Window(root)
#ser_port = serial.Serial(serial_port, 115200, timeout = 0.1)
#ser_port.write(b'\x03') #takes and puts value in byte format
#ser_port.write(b'\x04')

while(1):
    root.update_idletasks()
    root.update()
#    data = (ser_port.readline()).decode('UTF-8')
#    print(str(data))
