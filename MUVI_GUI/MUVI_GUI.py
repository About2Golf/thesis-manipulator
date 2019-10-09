# import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
# from PIL import Image, ImageTk
import serial
import time

config_file = None
serBuffer = ""

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -------------------------- Class Definitions --------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

class status_box():
    def __init__(self,frame, row, column, units, name):
        self.row = row
        self.column = column
        self.units = units
        self.name = name
        # self.POSITION = None
        # self.SPEED = None
        # self.DATUM = None
        self.status_frame = LabelFrame(frame, text=self.name, bg='white')
        self.status_frame.grid(row=self.row, column=self.column, rowspan=3, columnspan=3, sticky='WE', ipadx=5, ipady=5)

        self.pos_label = Label(self.status_frame, text="Position:", bg='white').grid(row=self.row,column=self.column, sticky=W)
        self.position = Entry(self.status_frame, width = 10, bg='gray80', justify='right')
        # self.position.insert(0, "0123")
        self.position.grid(row=self.row, column=self.column+1, sticky=E)
        self.pos_units = Label(self.status_frame, text=self.units, bg='white').grid(row=self.row,column=self.column+2, sticky=W)

        self.speed_label = Label(self.status_frame, text="Speed:", bg='white').grid(row=(self.row+1),column=self.column, sticky=W)
        self.speed = Entry(self.status_frame, width = 10, bg='gray80', justify='right')
        # self.speed.insert(0, "0123")
        self.speed.grid(row=(self.row+1), column=self.column+1, sticky=E)
        self.speed_units = Label(self.status_frame, text=(self.units+"/s"), bg='white').grid(row=(self.row+1),column=self.column+2, sticky=W)

        self.datum_label = Label(self.status_frame, text="Datum:", bg='white').grid(row=(self.row+2),column=self.column, sticky=W)
        self.datum = Entry(self.status_frame, width = 10, bg='gray80',  justify='right')
        # self.datum.insert(0, "0123")
        self.datum.grid(row=(self.row+2), column=self.column+1, sticky=E)
        self.pos_units = Label(self.status_frame, text=self.units, bg='white').grid(row=(self.row+2),column=self.column+2, sticky=W)

        self.m_lim_label = Label(self.status_frame, text="-Limit", bg='white').grid(row=(self.row+3),column=self.column, sticky=W)
        self.p_lim_label = Label(self.status_frame, text="+Limit", bg='white').grid(row=(self.row+3),column=self.column+1, sticky=E)

        self.m_limit_button = Canvas(self.status_frame, bg ='white', height = 30, width = 30,bd=0,highlightthickness=0)
        self.m_limit_button.grid(row=(self.row+4),column=self.column)
        self.m_lim = self.m_limit_button.create_oval(5,5,25,25, fill ='gray80')

        self.p_limit_button = Canvas(self.status_frame, bg ='white', height = 30, width = 30,bd=0,highlightthickness=0)
        self.p_limit_button.grid(row=(self.row+4),column=self.column+1, sticky=E)
        self.p_lim = self.p_limit_button.create_oval(5,5,25,25, fill ='gray80')

        self.mark_datum = Button(self.status_frame, text="Mark Datum", width=15, command=self.mark_datum)
        self.mark_datum.grid(row=self.row+5, column=self.column,columnspan=4, sticky=W)

    def limit_on(self, identifier):
        if identifier == 'p':
            self.p_limit_button.itemconfigure(self.p_lim, fill='red')
        elif identifier == 'm':
            self.m_limit_button.itemconfigure(self.m_lim, fill='red')

    def limit_off(self, identifier):
        if identifier == 'p':
            self.p_limit_button.itemconfigure(self.p_lim, fill='gray80')
        elif identifier == 'm':
            self.m_limit_button.itemconfigure(self.m_lim, fill='gray80')

    def update_position(self, position = None):
        self.position.delete(0, END)
        self.position.insert(0, str(position))

    def update_speed(self, speed = None):
        self.speed.delete(0, END)
        self.speed.insert(0, str(speed))

    def mark_datum(self):
        self.datum.delete(0, END)
        self.datum.insert(0, self.position.get())

    def update_datum(self, datum = None):
        self.datum.delete(0, END)
        self.datum.insert(0, str(datum))

    def get_datum(self):
        return self.datum.get()

class control_box():
    def __init__(self, frame, row, column, units, name, status_box):
        self.status_box = status_box
        self.row = row
        self.column = column
        self.units = units
        self.name = name
        self.TARGET = 0
        self.JOGSIZE = 0
        self.ENABLED = 0
        self.control_frame = LabelFrame(frame, text=self.name, bg='white')
        self.control_frame.grid(row=self.row, column=self.column, rowspan=3, columnspan=3, sticky='WE', ipadx=5, ipady=5)

        self.enable_label = Label(self.control_frame, text="Enable:", bg='white').grid(row=(self.row),column=self.column, sticky=W)
        self.enable_mot = Button(self.control_frame, text="OFF", width=8, command=self.toggle_enable)
        self.enable_mot.grid(row=self.row, column=self.column+1, sticky=E)

        self.targ_label = Label(self.control_frame, text="Target:", bg='white').grid(row=self.row+1,column=self.column, sticky=W)
        self.target = Entry(self.control_frame, width = 10, bg="white", justify='right')
        # self.position.insert(0, "0123")
        self.target.grid(row=self.row+1, column=self.column+1, sticky=E)
        self.targ_units = Label(self.control_frame, text=self.units, bg='white').grid(row=self.row+1,column=self.column+2,columnspan=2, sticky=W)

        self.jog_label = Label(self.control_frame, text="Jog Size:", bg='white').grid(row=(self.row+2),column=self.column, sticky=W)
        self.jog_size = Entry(self.control_frame, width = 10, bg="white", justify='right')
        # self.speed.insert(0, "0123")
        self.jog_size.grid(row=(self.row+2), column=self.column+1, sticky=E)
        self.jog_units = Label(self.control_frame, text=(self.units), bg='white').grid(row=(self.row+2),column=self.column+2,columnspan=2,  sticky=W)

        self.jog_m = Button(self.control_frame, text="Jog -", width=5, command=self.jog_m)
        self.jog_m.grid(row=self.row+3, column=self.column, sticky=W)

        self.jog_p = Button(self.control_frame, text="Jog +", width=5, command=self.jog_p)
        self.jog_p.grid(row=self.row+3, column=self.column+1, sticky=E)

        self.set_datum_to_targ = Button(self.control_frame, text="Set Datum to Target", width=15, command=self.set_datum_to_targ)
        self.set_datum_to_targ.grid(row=self.row+4, column=self.column,columnspan=4, sticky=W)

        self.set_zero = Button(self.control_frame, text= "Set Zero", width=15, command=self.set_zero)
        self.set_zero.grid(row=self.row+5, column=self.column,columnspan=4, sticky=W)

    def toggle_enable(self, force = 1, disable = 1):
        '''
        use
        t_btn.config('text')[-1]
        to get the present state of the toggle button
        '''
        if (self.enable_mot.config('text')[-1] == 'ON' or not force) and disable:
            self.enable_mot.config(text='OFF')
            self.ENABLED = 0
        else:
            self.enable_mot.config(text='ON')
            self.ENABLED = 1

    def jog_m(self):
        try:
            self.TARGET -= float(self.jog_size.get())
        except:
            print('Must enter number to target')
        self.update_target(round(self.TARGET,3))

    def jog_p(self):
        try:
            self.TARGET += float(self.jog_size.get())
        except:
            print('Must enter number to target')
        self.update_target(round(self.TARGET,3))

    def set_datum_to_targ(self):
        self.target.delete(0, END)
        self.target.insert(0, self.status_box.datum.get())

    def set_zero(self):
        self.target.delete(0, END)
        self.target.insert(0, '0')
        self.status_box.position.delete(0, END)
        self.status_box.position.insert(0, '0')

    def update_target(self, new_target):
        self.target.delete(0, END)
        self.target.insert(0, str(new_target))

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- Methods ---------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

def stop_manipulator():
    # code to stop manipulator
    x_control_frame.toggle_enable(force = 0, disable = 1)
    z_control_frame.toggle_enable(force = 0, disable = 1)
    y_control_frame.toggle_enable(force = 0, disable = 1)
    p_control_frame.toggle_enable(force = 0, disable = 1)
    messagebox.showinfo("Manipulator Status","Manipulator stopped by user.")

def ins_params():
    messagebox.showinfo("Instrument Parameters","Fill in parameters")

def browse_button():
    global config_file
    filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
    config_file = filename
    # print(config_file)
    config.delete(0, END)
    config.insert(0,str(config_file))

def FOV_sweep():
    messagebox.showinfo("Run Test","Sweeping FOV")

def boresight():
    messagebox.showinfo("Run Test","Boresight")

def SL_sweep():
    messagebox.showinfo("Run Test","Sweeping Stray Light")

def move_stages():
    messagebox.showinfo("Control","Moving stages")

def enable_all():
    x_control_frame.toggle_enable(disable=0)
    z_control_frame.toggle_enable(disable=0)
    y_control_frame.toggle_enable(disable=0)
    p_control_frame.toggle_enable(disable=0)

def zero_all():
    messagebox.showinfo("Control","Zeroing stages")

def set_motion_params():
    param_window = Toplevel()
    # messagebox.showinfo("Control","Set params")

def send_cmd():
    print('sent')
    # ser.write(cmd.get().encode())
    # ser.write(b'1')
    ser.write(bytes(cmd.get().encode('utf-8')))
    # messagebox.showinfo("Control","Sending command")

def log_print(to_print):
    log.insert(END, to_print)

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- GUI Window ------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
window = Tk()
window.title("MUVI User Interface")
window.configure(background='white')
window.geometry("1500x1000")

# Top Row
cal_poly_logo = PhotoImage(file = "cal_poly_me_logo.gif")
Label (window, image=cal_poly_logo, bg="white") .grid(row=0, column = 0, sticky = 'W')

Label(window, text="4 DOF \n Manipulator Interface", bg='white',font=(None, 15)).grid(row=0,column=3)

ucb_logo = PhotoImage(file = "SSL-Berkeley-80blue.gif")
Label (window, image=ucb_logo, bg="white") .grid(row=0, column = 5, sticky = 'E')

# Status Row
status_frame = LabelFrame(window, text="Status Panel", bg='white')
status_frame.grid(row=3, column=0, rowspan=5, columnspan=50, sticky='WE', ipadx=5, ipady=5)

x_status_frame = status_box(status_frame, 4, 0, "mm", "X Translation")
z_status_frame = status_box(status_frame, 4, 3, "mm", "Z Translation")
y_status_frame = status_box(status_frame, 4, 6, "deg", "Yaw Rotation")
p_status_frame = status_box(status_frame, 4, 9, "deg", "Pitch Rotation")

x_status_frame.update_position()
z_status_frame.update_position()
y_status_frame.update_position()
p_status_frame.update_position()

x_status_frame.update_speed()
z_status_frame.update_speed()
y_status_frame.update_speed()
p_status_frame.update_speed()

x_status_frame.update_datum()
z_status_frame.update_datum()
y_status_frame.update_datum()
p_status_frame.update_datum()

# x_status_frame.limit_on('p')

# Control Row
control_frame = LabelFrame(window, text="Control Panel", bg='white')
control_frame.grid(row=8, column=0, rowspan=5, columnspan=50, sticky='WE', ipadx=5, ipady=5)

Button(control_frame, text ="STOP", command = stop_manipulator, bg="red3", height=2, width=20).grid(row=1,column=0, sticky='W')

cmd_label = Label(control_frame, text="Send Command:", bg='white').grid(row=1,column=3, sticky=E)
cmd = Entry(control_frame, width = 25, bg="white", justify='right')
cmd.grid(row=1, column=4, columnspan = 4, sticky=W)
cmd.insert(0,'m;p;1000;1;50;6000;50')
# cmd.insert(0,'d;p')

Button(control_frame, text ="Send", command = send_cmd, height=2, width=20).grid(row=1,column=9, sticky='W')

Button(control_frame, text= "Move Stages", height=2, width=20, command=move_stages).grid(row=9, column=0, sticky=W)

Button(control_frame, text= "Enable All", height=2, width=20, command=enable_all).grid(row=9, column=3, sticky=W)

Button(control_frame, text= "Zero All", height=2, width=20, command=zero_all).grid(row=9, column=6, sticky=W)

Button(control_frame, text= "Set Motion Parameters", height=2, width=20, command=set_motion_params).grid(row=9, column=9, sticky=W)

x_control_frame = control_box(control_frame, 10, 0, "mm", "X Translation", x_status_frame)
z_control_frame = control_box(control_frame, 10, 3, "mm", "Z Translation", z_status_frame)
y_control_frame = control_box(control_frame, 10, 6, "deg", "Yaw Rotation", y_status_frame)
p_control_frame = control_box(control_frame, 10, 9, "deg", "Pitch Rotation", p_status_frame)

# Run Test Row
test_frame = LabelFrame(window, text="Run Test", bg='white')
test_frame.grid(row=25, column=0, columnspan=50, sticky='WE', ipadx=5, ipady=5)

Button(test_frame, text= "Instrument Parameters", width=20, command=ins_params).grid(row=26, column=1, sticky=W)

config_label = Label(test_frame, text="Config File:", bg='white').grid(row=26,column=2, sticky=E)
config = Entry(test_frame, width = 60, bg="white", justify='right')
config.grid(row=26, column=3, columnspan = 3, sticky=W)

Button(test_frame, text= "Browse File", width=12, command=browse_button).grid(row=26, column=6, sticky=E)

Button(test_frame, text= "FOV Sweep", width=20, command=FOV_sweep).grid(row=27, column=1, sticky=W)

Button(test_frame, text= "Boresight", width=20, command=boresight).grid(row=27, column=3, sticky=W)

Button(test_frame, text= "Stray Light Sweep", width=20, command=SL_sweep).grid(row=27, column=5, sticky=W)

Label(window, text="Created by: Jason Grillo \n Cal Poly Mechanical Engineering \n In Collaboration with UCB Space Sciences Laboratories \n \u00A9 2019", bg='white',font=(None, 10)).grid(row=28,column=3)


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- Run the GUI -----------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

# Credit to: https://robotic-controls.com/learn/python-guis/tkinter-serial

log = Text (window, width=80, height=30, takefocus=0, bg='white')
log.grid(row=0,rowspan=10, column = 60, sticky = E)

# serialPort = "COM6"
serialPort = "COM7"
baudRate = 115200
try:
    ser = serial.Serial(serialPort , baudRate, timeout=0, writeTimeout=0,dsrdtr=True) #ensure non-blocking
    ser.setDTR(True)
    # ser.flush()
    # ser.write(b'\x03') #takes and puts value in byte format
    # ser.write(b'\x04')
    # ser.write(b'hello')
except:
    log_print("Unable to open Serial Port")

serBuffer = ""

def readSerial():
    while True:
        c = ser.read().decode("utf-8") # attempt to read a character from Serial
        #was anything read?
        if len(c) == 0:
            break
        # get the buffer from outside of this function
        global serBuffer
        # check if character is a delimeter
        if c == '\r':
            c = '' # don't want returns. chuck it
        if c == '\n':
            serBuffer += "\n" # add the newline to the buffer
            #add the line to the TOP of the log
            log_print(serBuffer)
            # log.insert(END, serBuffer)
            # log.insert('0.0', serBuffer)
            serBuffer = "" # empty the buffer
        else:
            serBuffer += c # add to the buffer
    window.after(10, readSerial) # check serial again soon

# after initializing serial, an arduino may need a bit of time to reset
window.after(100, readSerial)

window.mainloop()


# move command: m;p;1000;1;50;6000;50
