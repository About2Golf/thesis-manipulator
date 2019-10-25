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
        self.status_frame.grid(row=self.row, column=self.column, rowspan=3, columnspan=3, sticky='WE', padx=5, pady=5)

        self.pos_label = Label(self.status_frame, text="Position:", bg='white').grid(row=self.row,column=self.column, sticky=W, padx=5, pady=1)
        self.position = Entry(self.status_frame, width = 10, bg='gray80', justify='right')
        # self.position.insert(0, "0123")
        self.position.grid(row=self.row, column=self.column+1, sticky=E)
        self.pos_units = Label(self.status_frame, text=self.units, bg='white').grid(row=self.row,column=self.column+2, sticky=W)

        self.speed_label = Label(self.status_frame, text="Speed:", bg='white').grid(row=(self.row+1),column=self.column, sticky=W, padx=5, pady=1)
        self.speed = Entry(self.status_frame, width = 10, bg='gray80', justify='right')
        # self.speed.insert(0, "0123")
        self.speed.grid(row=(self.row+1), column=self.column+1, sticky=E)
        self.speed_units = Label(self.status_frame, text=(self.units+"/s"), bg='white').grid(row=(self.row+1),column=self.column+2, sticky=W)

        self.mark_label = Label(self.status_frame, text="Mark:", bg='white').grid(row=(self.row+2),column=self.column, sticky=W, padx=5, pady=1)
        self.mark = Entry(self.status_frame, width = 10, bg='gray80',  justify='right')
        # self.mark.insert(0, "0123")
        self.mark.grid(row=(self.row+2), column=self.column+1, sticky=E)
        self.pos_units = Label(self.status_frame, text=self.units, bg='white').grid(row=(self.row+2),column=self.column+2, sticky=W)

        self.m_lim_label = Label(self.status_frame, text="-Limit", bg='white').grid(row=(self.row+3),column=self.column, sticky=W, padx=5, pady=1)
        self.p_lim_label = Label(self.status_frame, text="+Limit", bg='white').grid(row=(self.row+3),column=self.column+1, sticky=E, padx=5, pady=1)

        self.m_limit_button = Canvas(self.status_frame, bg ='white', height = 30, width = 30,bd=0,highlightthickness=0)
        self.m_limit_button.grid(row=(self.row+4),column=self.column, padx=10)
        self.m_lim = self.m_limit_button.create_oval(5,5,25,25, fill ='gray80')

        self.p_limit_button = Canvas(self.status_frame, bg ='white', height = 30, width = 30,bd=0,highlightthickness=0)
        self.p_limit_button.grid(row=(self.row+4),column=self.column+1, sticky=E, padx=10)
        self.p_lim = self.p_limit_button.create_oval(5,5,25,25, fill ='gray80')

        self.mark_mark = Button(self.status_frame, text="Mark Position", width=15, command=self.mark_mark, bg='deep sky blue')
        self.mark_mark.grid(row=self.row+5, column=self.column,columnspan=4, sticky=W, padx=25, pady=1)

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

    def mark_mark(self):
        self.mark.delete(0, END)
        self.mark.insert(0, self.position.get())

    def update_mark(self, mark = None):
        self.mark.delete(0, END)
        self.mark.insert(0, str(mark))

    def get_mark(self):
        return self.mark.get()

class control_box():
    def __init__(self, frame, row, column, units, name, status_box, stage):
        self.status_box = status_box
        self.row = row
        self.column = column
        self.units = units
        self.name = name
        self.stage = stage
        self.TARGET = 0
        self.JOGSIZE = 0
        self.ENABLED = 0
        self.control_frame = LabelFrame(frame, text=self.name, bg='white')
        self.control_frame.grid(row=self.row, column=self.column, rowspan=3, columnspan=3, sticky='WE', padx=5, pady=5)

        self.enable_label = Label(self.control_frame, text="Enable:", bg='white').grid(row=(self.row),column=self.column, sticky=W, padx=5, pady=1)
        self.enable_mot = Button(self.control_frame, text="OFF", width=8, command=self.toggle_enable)
        self.enable_mot.grid(row=self.row, column=self.column+1, sticky=E, pady=2)

        self.targ_label = Label(self.control_frame, text="Target:", bg='white').grid(row=self.row+1,column=self.column, sticky=W, padx=5, pady=1)
        self.target = Entry(self.control_frame, width = 10, bg="white", justify='right')
        # self.position.insert(0, "0123")
        self.target.grid(row=self.row+1, column=self.column+1, sticky=E)
        self.targ_units = Label(self.control_frame, text=self.units, bg='white').grid(row=self.row+1,column=self.column+2,columnspan=2, sticky=W)

        self.jog_label = Label(self.control_frame, text="Jog Size:", bg='white').grid(row=(self.row+2),column=self.column, sticky=W, padx=5, pady=1)
        self.jog_size = Entry(self.control_frame, width = 10, bg="white", justify='right')
        # self.speed.insert(0, "0123")
        self.jog_size.grid(row=(self.row+2), column=self.column+1, sticky=E)
        self.jog_units = Label(self.control_frame, text=(self.units), bg='white').grid(row=(self.row+2),column=self.column+2,columnspan=2,  sticky=W)

        self.move_stage = Button(self.control_frame, text="Move Stage", width=15, command=self.move_stage)
        self.move_stage.grid(row=self.row+3, column=self.column,columnspan=4, sticky=W, padx=20, pady=3)

        self.jog_m = Button(self.control_frame, text="Jog -", width=5, command=self.jog_m)
        self.jog_m.grid(row=self.row+4, column=self.column, sticky=W, padx=(20,0), pady=3)

        self.jog_p = Button(self.control_frame, text="Jog +", width=5, command=self.jog_p)
        self.jog_p.grid(row=self.row+4, column=self.column+1, sticky=W, padx=(25,0), pady=3)

        self.set_mark_to_targ = Button(self.control_frame, text="Put Mark to Target", width=15, command=self.set_mark_to_targ)
        self.set_mark_to_targ.grid(row=self.row+5, column=self.column,columnspan=4, sticky=W, padx=20, pady=3)

        self.set_zero = Button(self.control_frame, text= "Set Zero", width=15, command=self.set_zero)
        self.set_zero.grid(row=self.row+6, column=self.column,columnspan=4, sticky=W, padx=20, pady=3)

    def toggle_enable(self, force = 1, disable = 1):
        '''
        use
        t_btn.config('text')[-1]
        to get the present state of the toggle button
        '''
        if (self.enable_mot.config('text')[-1] == 'ON' or not force) and disable:
            toggle_string = 'd;' + self.stage
            ser.write(bytes(toggle_string.encode('utf-8')))
            self.enable_mot.config(text='OFF')
            self.ENABLED = 0
        else:
            toggle_string = 'e;' + self.stage
            ser.write(bytes(toggle_string.encode('utf-8')))
            self.enable_mot.config(text='ON')
            self.ENABLED = 1
    #
    # def update_stage_enable(self, value)
    #

    def move_stage(self):
        gui_print('moving stage')

    def jog_m(self):
        try:
            self.TARGET -= float(self.jog_size.get())
        except:
            gui_print('Must enter number to target')
        self.update_target(round(self.TARGET,3))

    def jog_p(self):
        try:
            self.TARGET += float(self.jog_size.get())
        except:
            gui_print('Must enter number to target')
        self.update_target(round(self.TARGET,3))

    def set_mark_to_targ(self):
        self.target.delete(0, END)
        self.target.insert(0, self.status_box.mark.get())

    def set_zero(self):
        self.target.delete(0, END)
        self.target.insert(0, '0')
        self.status_box.position.delete(0, END)
        self.status_box.position.insert(0, '0')

    def update_target(self, new_target):
        self.target.delete(0, END)
        self.target.insert(0, str(new_target))

    def get_target(self):
        return float(self.target.get())

    def set_jogsize(self, new_jogsize):
        self.jog_size.delete(0, END)
        self.jog_size.insert(0, str(new_jogsize))

    def get_enable(self):
        return self.ENABLED

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- Methods ---------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

def stop_manipulator():
    ser.write(bytes('a;a'.encode('utf-8')))
    x_control_frame.toggle_enable(force = 0, disable = 1)
    z_control_frame.toggle_enable(force = 0, disable = 1)
    y_control_frame.toggle_enable(force = 0, disable = 1)
    p_control_frame.toggle_enable(force = 0, disable = 1)
    messagebox.showinfo("Manipulator Status","Manipulator stopped by user.")
    GUI_STATE = 0
    MOTOR_MASK = 0b0000  # x;z;y;p
    ACK = None
    EXECUTING = False
    MOVE_NUM = 1
    SET_MICROSTEP = True

def ins_params():
    messagebox.showinfo("Instrument Parameters","Fill in parameters")

def browse_button():
    # global config_file
    filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
    print(filename)
    # config_file = filename
    # print(config_file)
    config.delete(0, END)
    config.insert(0,str(filename))

def FOV_sweep():
    messagebox.showinfo("Run Test","Sweeping FOV")

def boresight():
    messagebox.showinfo("Run Test","Boresight")

def SL_sweep():
    messagebox.showinfo("Run Test","Sweeping Stray Light")

def move_stages():
    global MOTOR_MASK, GUI_STATE, EXECUTING, MOVE_NUM
    global x_pos, z_pos, y_pos, p_pos, x_target, z_target, y_target, p_target
    if not EXECUTING:
        x_target = x_control_frame.get_target()
        z_target = z_control_frame.get_target()
        y_target = y_control_frame.get_target()
        p_target = p_control_frame.get_target()
        if not x_pos == x_target and x_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,3)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,3)
        if not z_pos == z_target and z_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,2)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,2)
        if not y_pos == y_target and y_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,1)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,1)
        if not p_pos == p_target and p_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,0)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,0)
        MOVE_NUM = 1
        GUI_STATE = 3
        EXECUTING = True
    else:
        return

def enable_all():
    global MOTOR_MASK, GUI_STATE, EXECUTING
    if not EXECUTING:
        MOTOR_MASK = 0b1111
        GUI_STATE = 2
        EXECUTING = True
    else:
        return

def zero_all():
    global MOTOR_MASK, GUI_STATE, EXECUTING, ZERO_SEQ, SET_MICROSTEP, ZEROING, DISABLED, ZERO_SENT, SET_ENABLE, MOVE_TO_DATUM
    if not EXECUTING:
        if x_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,3)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,3)
        if z_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,2)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,2)
        if y_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,1)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,1)
        if p_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,0)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,0)
        GUI_STATE = 4
        EXECUTING = True
        ZERO_SEQ = 1
        SET_MICROSTEP = True
        # ZEROING = False
        # DISABLED = False
        # ZERO_SENT = False
        # SET_ENABLE = True
        # MOVE_TO_DATUM = False
    else:
        return


import csv

class CSV_Read():
    def __init__(self, filename):
        with open(filename, "r") as f_input:
            csv_input = csv.reader(f_input)
            self.details = list(csv_input)

    def get_col_row(self, col, row):
        return self.details[row-1][col-1]

# data = ContactDetails("input.csv")
#
# phone_number = data.get_col_row(5, 4)
# name = data.get_col_row(2,4)
# last_name = data.get_col_row(3,4)
#
# print "%s %s: %s" % (name, last_name, phone_number)


def set_motion_params():
    global motion_params
    motion_filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
    motion_params = CSV_Read(motion_filename)
    print(motion_params.get_col_row(1,2))
    # print(motion_filename)
    # param_window = Toplevel()
    # messagebox.showinfo("Control","Set params")

def send_cmd():
    gui_print('sent')
    ser.write(bytes(cmd.get().encode('utf-8')))

def reset():
    global x_pos_true, z_pos_true, y_pos_true, p_pos_true
    global x_dir, z_dir, y_dir, p_dir, x_pos, z_pos, y_pos, p_pos
    global prev_x_pos, prev_z_pos, prev_y_pos, prev_p_pos
    global x_speed, z_speed, y_speed, p_speed
    global x_lim, z_lim, y_lim, p_lim, x_target, z_target, y_target, p_target
    global GUI_STATE, MOTOR_MASK, ACK, EXECUTING, MOVE_NUM, SET_MICROSTEP
    ser.write(b'r;a')
    x_pos_true = 0.0
    z_pos_true = 0.0
    y_pos_true = 0.0
    p_pos_true = 0.0
    x_dir = 0
    z_dir = 0
    y_dir = 0
    p_dir = 0
    x_pos = 0.0
    z_pos = 0.0
    y_pos = 0.0
    p_pos = 0.0
    prev_x_pos = 0.0
    prev_z_pos = 0.0
    prev_y_pos = 0.0
    prev_p_pos = 0.0
    x_speed = 0.0
    z_speed = 0.0
    y_speed = 0.0
    p_speed = 0.0
    x_lim = 0
    z_lim = 0
    y_lim = 0
    p_lim = 0
    x_target = 0.0
    z_target = 0.0
    y_target = 0.0
    p_target = 0.0
    GUI_STATE = 0
    MOTOR_MASK = 0b0000  # x;z;y;p
    ACK = None
    EXECUTING = False
    MOVE_NUM = 1
    SET_MICROSTEP = True

x_pos_true = 0.0
z_pos_true = 0.0
y_pos_true = 0.0
p_pos_true = 0.0

x_dir = 0
z_dir = 0
y_dir = 0
p_dir = 0

x_pos = 0.0
z_pos = 0.0
y_pos = 0.0
p_pos = 0.0
prev_x_pos = 0.0
prev_z_pos = 0.0
prev_y_pos = 0.0
prev_p_pos = 0.0
x_speed = 0.0
z_speed = 0.0
y_speed = 0.0
p_speed = 0.0
x_lim = 0
z_lim = 0
y_lim = 0
p_lim = 0

x_target = 0.0
z_target = 0.0
y_target = 0.0
p_target = 0.0

x_jog = 0.0
z_jog = 0.0
y_jog = 0.0
p_jog = 0.0

X_STOPPED = True

GUI_STATE = 0
prev_GUI_STATE = 0
MOTOR_MASK = 0b0000  # x;z;y;p
ACK = None
EXECUTING = False
MOVE_NUM = 1
ZERO_SEQ = 1
SET_MICROSTEP = True
ZEROING = False
DISABLED = False
ZERO_SENT = False
SET_ENABLE = True
X_MICROSTEP_SET = False
MOVE_TO_DATUM = False

def read_data():
    global serBuffer, MOVE_NUM, ACK, x_dir, z_dir, y_dir, p_dir
    global lin_Pitch, lin_motor_steps, rot_gear_ratio, rot_motor_steps
    global move1_microsteps, move2_microsteps
    global x_pos_true, z_pos_true, y_pos_true, p_pos_true
    global x_direction_param, z_direction_param, y_direction_param, p_direction_param
    log_print(serBuffer)
    # uC_resp = serBuffer[1::] # remove first character (b)
    # uC_resp = uC_resp[1::] # remove first character (')
    uC_resp = serBuffer[:-1:] # remove last character (/n)
    # uC_resp = uC_resp[:-1:] # remove last character (')
    uC_resp = uC_resp.split(';')
    if not (' ' in uC_resp[0]):
        if not uC_resp[0].isalpha() and len(uC_resp)>1:
            return uC_resp
        else:
            ACK = uC_resp[0]
            if ACK == 's':
                if uC_resp[1] == 'x':
                    if MOVE_NUM == 1:
                        x_pos_true += x_direction_param*x_dir*float(uC_resp[2])*lin_Pitch/(move1_microsteps*lin_motor_steps)
                    elif MOVE_NUM == 2:
                        x_pos_true += x_direction_param*x_dir*float(uC_resp[2])*lin_Pitch/(move2_microsteps*lin_motor_steps)
                elif uC_resp[1] == 'z':
                    if MOVE_NUM == 1:
                        z_pos_true += z_direction_param*z_dir*float(uC_resp[2])*lin_Pitch/(move1_microsteps*lin_motor_steps)
                    elif MOVE_NUM == 2:
                        z_pos_true += z_direction_param*z_dir*float(uC_resp[2])*lin_Pitch/(move2_microsteps*lin_motor_steps)
                elif uC_resp[1] == 'y':
                    if MOVE_NUM == 1:
                        y_pos_true += y_direction_param*y_dir*float(uC_resp[2])*360/(rot_gear_ratio*move1_microsteps*rot_motor_steps)
                    elif MOVE_NUM == 2:
                        y_pos_true += y_direction_param*y_dir*float(uC_resp[2])*360/(rot_gear_ratio*move2_microsteps*rot_motor_steps)
                elif uC_resp[1] == 'p':
                    if MOVE_NUM == 1:
                        p_pos_true += p_direction_param*p_dir*float(uC_resp[2])*360/(rot_gear_ratio*move1_microsteps*rot_motor_steps)
                    elif MOVE_NUM == 2:
                        p_pos_true += p_direction_param*p_dir*float(uC_resp[2])*360/(rot_gear_ratio*move2_microsteps*rot_motor_steps)
                gui_print(y_pos_true)
            return None

def GUI_state_machine():
    # global GUI_STATE, prev_GUI_STATE, MOTOR_MASK, ACK, EXECUTING
    global GUI_STATE, prev_GUI_STATE, MOTOR_MASK, ACK, EXECUTING, MOVE_NUM, ZERO_SEQ
    global SET_MICROSTEP, ZEROING, DISABLED, ZERO_SENT, SET_ENABLE, MOVE_TO_DATUM
    global X_MICROSTEP_SET
    global x_target, z_target, y_target, p_target
    global x_datum_offset, z_datum_offset, y_datum_offset, p_datum_offset
    global x_lim, z_lim, y_lim, p_lim
    global X_STOPPED
    global x_direction_param, z_direction_param, y_direction_param, p_direction_param

    parsed = read_data()
    if parsed:
        update_status(parsed)
    # print(GUI_STATE)

    # IDLE
    if GUI_STATE == 0:
        ACK = None  # need this to clear previous ack when executing done
        return

    # WAIT FOR ACK
    elif GUI_STATE == 1:
        if ACK == 'e':
            GUI_STATE = prev_GUI_STATE
            # prev_GUI_STATE = 1
            ACK = None
        elif ACK == 's':
            MOVE_NUM += 1
            SET_MICROSTEP = True
            GUI_STATE = prev_GUI_STATE
            ACK = None
        elif ACK == 't':
            GUI_STATE = prev_GUI_STATE
            SET_MICROSTEP = False
            ACK = None
        elif ACK == 'd':
            GUI_STATE = prev_GUI_STATE
            ACK = None
        elif ACK == 'z':
            GUI_STATE = prev_GUI_STATE
            ACK = None

    # SENDING ENABLE
    elif GUI_STATE == 2:
        if testBit(MOTOR_MASK,3):
            x_control_frame.toggle_enable(disable=0)
            MOTOR_MASK = clearBit(MOTOR_MASK,3)
            # prev_GUI_STATE = 2
            GUI_STATE = 1
        elif testBit(MOTOR_MASK,2):
            z_control_frame.toggle_enable(disable=0)
            MOTOR_MASK = clearBit(MOTOR_MASK,2)
            # prev_GUI_STATE = 2
            GUI_STATE = 1
        elif testBit(MOTOR_MASK,1):
            y_control_frame.toggle_enable(disable=0)
            MOTOR_MASK = clearBit(MOTOR_MASK,1)
            # prev_GUI_STATE = 2
            GUI_STATE = 1
        elif testBit(MOTOR_MASK,0):
            p_control_frame.toggle_enable(disable=0)
            MOTOR_MASK = clearBit(MOTOR_MASK,0)
            # prev_GUI_STATE = 2
            GUI_STATE = 1
        else:
            # prev_GUI_STATE = 2
            GUI_STATE = 0
            EXECUTING = False
        prev_GUI_STATE = 2

    # MOVING STAGES
    elif GUI_STATE == 3:
        if testBit(MOTOR_MASK,3):
            # if x_control_frame.get_enable():
            if MOVE_NUM == 1:
                if SET_MICROSTEP:
                    set_microstep('x', move1_microsteps)
                    X_MICROSTEP_SET = False
                    GUI_STATE = 1
                else:
                    move('x', 1)
                    GUI_STATE = 1
            elif MOVE_NUM == 2:
                if SET_MICROSTEP:
                    set_microstep('x', move2_microsteps)
                    X_MICROSTEP_SET = True
                    GUI_STATE = 1
                else:
                    move('x', 2)
                    GUI_STATE = 1
            elif MOVE_NUM == 3:
                MOTOR_MASK = clearBit(MOTOR_MASK,3)
                MOVE_NUM = 1
            # else:
            #     MOTOR_MASK = clearBit(MOTOR_MASK,3)
            #     log_print('X Stepper is disabled. Click Enable and try again.\n')
        elif testBit(MOTOR_MASK,2):
            # if z_control_frame.get_enable():
            if MOVE_NUM == 1:
                if SET_MICROSTEP:
                    set_microstep('z', move1_microsteps)
                    GUI_STATE = 1
                else:
                    move('z', 1)
                    GUI_STATE = 1
            elif MOVE_NUM == 2:
                if SET_MICROSTEP:
                    set_microstep('z', move2_microsteps)
                    GUI_STATE = 1
                else:
                    move('z', 2)
                    GUI_STATE = 1
            elif MOVE_NUM == 3:
                MOTOR_MASK = clearBit(MOTOR_MASK,2)
                MOVE_NUM = 1
            # else:
            #     MOTOR_MASK = clearBit(MOTOR_MASK,2)
            #     log_print('Z Stepper is disabled. Click Enable and try again.\n')
        elif testBit(MOTOR_MASK,1):
            # if y_control_frame.get_enable():
            if MOVE_NUM == 1:
                if SET_MICROSTEP:
                    set_microstep('y', move1_microsteps)
                    GUI_STATE = 1
                else:
                    move('y', 1)
                    GUI_STATE = 1
            elif MOVE_NUM == 2:
                if SET_MICROSTEP:
                    set_microstep('y', move2_microsteps)
                    GUI_STATE = 1
                else:
                    move('y', 2)
                    GUI_STATE = 1
            elif MOVE_NUM == 3:
                MOTOR_MASK = clearBit(MOTOR_MASK,1)
                MOVE_NUM = 1
            # else:
            #     MOTOR_MASK = clearBit(MOTOR_MASK,1)
            #     log_print('Y Stepper is disabled. Click Enable and try again.\n')
        elif testBit(MOTOR_MASK,0):
            # if p_control_frame.get_enable():
            if MOVE_NUM == 1:
                if SET_MICROSTEP:
                    set_microstep('p', move1_microsteps)
                    GUI_STATE = 1
                else:
                    move('p', 1)
                    GUI_STATE = 1
            elif MOVE_NUM == 2:
                if SET_MICROSTEP:
                    set_microstep('p', move2_microsteps)
                    GUI_STATE = 1
                else:
                    move('p', 2)
                    GUI_STATE = 1
            elif MOVE_NUM == 3:
                MOTOR_MASK = clearBit(MOTOR_MASK,0)
                MOVE_NUM = 1
            # else:
            #     MOTOR_MASK = clearBit(MOTOR_MASK,0)
            #     log_print('P Stepper is disabled. Click Enable and try again.\n')
        else:
            # prev_GUI_STATE = 2
            GUI_STATE = 0
            EXECUTING = False
        prev_GUI_STATE = 3

    # ZEROING STAGES
    elif GUI_STATE == 4:
        if testBit(MOTOR_MASK,3):
            if ZERO_SEQ == 1:
                if X_MICROSTEP_SET:
                # if X_MICROSTEP_SET and SET_MICROSTEP:
                    gui_print('setting move1 uS')
                    set_microstep('x', move1_microsteps)
                    X_MICROSTEP_SET = False
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                else:
                    ZERO_SEQ += 1
            elif ZERO_SEQ == 2:
                # if not ZEROING:
                    # move('x', 1)
                gui_print('zeroing')
                move('x', 1, zero = True)
                # ZEROING = True
                ZERO_SEQ += 1
                SET_MICROSTEP = True # set this for when it needs to move to Datum
                    # GUI_STATE = 1
            elif ZERO_SEQ == 3:
                # if abs(x_lim) and X_STOPPED:
                if abs(x_lim):
                    # if not DISABLED:
                    # time.sleep(1.5)
                    x_control_frame.toggle_enable(force = 0, disable = 1)
                    gui_print('disabling motor')
                    DISABLED = True
                    ZERO_SEQ += 1
                    GUI_STATE = 1
            elif ZERO_SEQ == 4:
                # if not ZERO_SENT:
                gui_print('zeroing encoder')
                ser.write(bytes('z;x'.encode('utf-8')))
                x_pos_true = x_direction_param*x_datum_offset
                # ZERO_SENT = True
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 5:
                # if DISABLED and SET_ENABLE:
                gui_print('enabling motor')
                # ACK = None
                x_control_frame.toggle_enable(disable=0)
                # SET_ENABLE = False
                # MOVE_TO_DATUM = True
                MOVE_NUM = 1
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 6:
                if MOVE_NUM == 1:
                    ACK = None
                    gui_print('moving to datum 1')
                    move('x', 1, to_datum = True)
                    GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if SET_MICROSTEP:
                        gui_print('setting move2 uS')
                        set_microstep('x', move2_microsteps)
                        X_MICROSTEP_SET = True
                        GUI_STATE = 1
                    else:
                        gui_print('moving to datum 2')
                        move('x', 2, to_datum = True)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    gui_print('resetting params for next zero')
                    MOTOR_MASK = clearBit(MOTOR_MASK,3)
                    MOVE_NUM = 1
                    ZERO_SEQ = 1
                    SET_MICROSTEP = True
                    # ZEROING = False
                    # DISABLED = False
                    # ZERO_SENT = False
                    # MOVE_TO_DATUM = False
            # if X_MICROSTEP_SET and SET_MICROSTEP:
            #     print('setting move1 uS')
            #     set_microstep('x', move1_microsteps)
            #     X_MICROSTEP_SET = False
            #     GUI_STATE = 1
            # if not ZEROING:
            #     # move('x', 1)
            #     print('zeroing')
            #     move('x', 1, zero = True)
            #     ZEROING = True
            #     SET_MICROSTEP = True # set this for when it needs to move to Datum
            #     # GUI_STATE = 1
            # else:
            #     if abs(x_lim) and not MOVE_TO_DATUM:
            #         if not DISABLED:
            #             print('disabling motor')
            #             x_control_frame.toggle_enable(force = 0, disable = 1)
            #             DISABLED = True
            #             GUI_STATE = 1
            #         else:
            #             if not ZERO_SENT:
            #                 print('zeroing encoder')
            #                 ser.write(bytes('z;x'.encode('utf-8')))
            #                 ZERO_SENT = True
            #                 GUI_STATE = 1
            #             elif DISABLED and SET_ENABLE:
            #                 print('enabling motor')
            #                 x_control_frame.toggle_enable(disable=0)
            #                 SET_ENABLE = False
            #                 MOVE_TO_DATUM = True
            #                 MOVE_NUM = 1
            #                 GUI_STATE = 1
            #     if MOVE_TO_DATUM:
            #         if MOVE_NUM == 1:
            #             print('moving to datum 1')
            #             move('x', 1, to_datum = True)
            #             GUI_STATE = 1
            #         elif MOVE_NUM == 2:
            #             if SET_MICROSTEP:
            #                 print('setting move2 uS')
            #                 set_microstep('x', move2_microsteps)
            #                 X_MICROSTEP_SET = True
            #                 GUI_STATE = 1
            #             else:
            #                 print('moving to datum 2')
            #                 move('x', 2, to_datum = True)
            #                 GUI_STATE = 1
            #         elif MOVE_NUM == 3:
            #             print('resetting params for next zero')
            #             MOTOR_MASK = clearBit(MOTOR_MASK,3)
            #             MOVE_NUM = 1
            #             SET_MICROSTEP = True
            #             ZEROING = False
            #             DISABLED = False
            #             ZERO_SENT = False
            #             MOVE_TO_DATUM = False
                    # else:
                    #     MOTOR_MASK = clearBit(MOTOR_MASK,3)
                    #     MOVE_NUM = 1
                    #     SET_MICROSTEP = True
                    #     ZEROING = False
                    #     DISABLED = False
                    #     ZERO_SENT = False
        # elif testBit(MOTOR_MASK,2):
        elif testBit(MOTOR_MASK,2):
            if ZERO_SEQ == 1:
                if Z_MICROSTEP_SET:
                # if X_MICROSTEP_SET and SET_MICROSTEP:
                    gui_print('setting move1 uS')
                    set_microstep('z', move1_microsteps)
                    Z_MICROSTEP_SET = False
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                else:
                    ZERO_SEQ += 1
            elif ZERO_SEQ == 2:
                # if not ZEROING:
                    # move('x', 1)
                gui_print('zeroing')
                move('z', 1, zero = True)
                # ZEROING = True
                ZERO_SEQ += 1
                SET_MICROSTEP = True # set this for when it needs to move to Datum
                    # GUI_STATE = 1
            elif ZERO_SEQ == 3:
                # if abs(x_lim) and X_STOPPED:
                if abs(z_lim):
                    # if not DISABLED:
                    # time.sleep(1.5)
                    z_control_frame.toggle_enable(force = 0, disable = 1)
                    gui_print('disabling motor')
                    DISABLED = True
                    ZERO_SEQ += 1
                    GUI_STATE = 1
            elif ZERO_SEQ == 4:
                # if not ZERO_SENT:
                gui_print('zeroing encoder')
                ser.write(bytes('z;z'.encode('utf-8')))
                z_pos_true = z_direction_param*z_datum_offset
                # ZERO_SENT = True
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 5:
                # if DISABLED and SET_ENABLE:
                gui_print('enabling motor')
                # ACK = None
                z_control_frame.toggle_enable(disable=0)
                # SET_ENABLE = False
                # MOVE_TO_DATUM = True
                MOVE_NUM = 1
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 6:
                if MOVE_NUM == 1:
                    ACK = None
                    gui_print('moving to datum 1')
                    move('z', 1, to_datum = True)
                    GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if SET_MICROSTEP:
                        gui_print('setting move2 uS')
                        set_microstep('z', move2_microsteps)
                        Z_MICROSTEP_SET = True
                        GUI_STATE = 1
                    else:
                        gui_print('moving to datum 2')
                        move('z', 2, to_datum = True)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    gui_print('resetting params for next zero')
                    MOTOR_MASK = clearBit(MOTOR_MASK,2)
                    MOVE_NUM = 1
                    ZERO_SEQ = 1
                    SET_MICROSTEP = True
        # elif testBit(MOTOR_MASK,1):
        elif testBit(MOTOR_MASK,1):
            if ZERO_SEQ == 1:
                if Y_MICROSTEP_SET:
                # if X_MICROSTEP_SET and SET_MICROSTEP:
                    gui_print('setting move1 uS')
                    set_microstep('y', move1_microsteps)
                    Y_MICROSTEP_SET = False
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                else:
                    ZERO_SEQ += 1
            elif ZERO_SEQ == 2:
                # if not ZEROING:
                    # move('x', 1)
                gui_print('zeroing')
                move('y', 1, zero = True)
                # ZEROING = True
                ZERO_SEQ += 1
                SET_MICROSTEP = True # set this for when it needs to move to Datum
                    # GUI_STATE = 1
            elif ZERO_SEQ == 3:
                # if abs(x_lim) and X_STOPPED:
                if abs(y_lim):
                    # if not DISABLED:
                    # time.sleep(1.5)
                    y_control_frame.toggle_enable(force = 0, disable = 1)
                    gui_print('disabling motor')
                    DISABLED = True
                    ZERO_SEQ += 1
                    GUI_STATE = 1
            elif ZERO_SEQ == 4:
                # if not ZERO_SENT:
                gui_print('zeroing encoder')
                ser.write(bytes('z;y'.encode('utf-8')))
                y_pos_true = y_direction_param*y_datum_offset
                # ZERO_SENT = True
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 5:
                # if DISABLED and SET_ENABLE:
                gui_print('enabling motor')
                # ACK = None
                y_control_frame.toggle_enable(disable=0)
                # SET_ENABLE = False
                # MOVE_TO_DATUM = True
                MOVE_NUM = 1
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 6:
                if MOVE_NUM == 1:
                    ACK = None
                    gui_print('moving to datum 1')
                    move('y', 1, to_datum = True)
                    GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if SET_MICROSTEP:
                        gui_print('setting move2 uS')
                        set_microstep('y', move2_microsteps)
                        X_MICROSTEP_SET = True
                        GUI_STATE = 1
                    else:
                        gui_print('moving to datum 2')
                        move('y', 2, to_datum = True)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    gui_print('resetting params for next zero')
                    MOTOR_MASK = clearBit(MOTOR_MASK,1)
                    MOVE_NUM = 1
                    ZERO_SEQ = 1
                    SET_MICROSTEP = True
        # elif testBit(MOTOR_MASK,0):
        if testBit(MOTOR_MASK,0):
            if ZERO_SEQ == 1:
                if P_MICROSTEP_SET:
                # if X_MICROSTEP_SET and SET_MICROSTEP:
                    gui_print('setting move1 uS')
                    set_microstep('p', move1_microsteps)
                    P_MICROSTEP_SET = False
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                else:
                    ZERO_SEQ += 1
            elif ZERO_SEQ == 2:
                # if not ZEROING:
                    # move('x', 1)
                gui_print('zeroing')
                move('p', 1, zero = True)
                # ZEROING = True
                ZERO_SEQ += 1
                SET_MICROSTEP = True # set this for when it needs to move to Datum
                    # GUI_STATE = 1
            elif ZERO_SEQ == 3:
                # if abs(x_lim) and X_STOPPED:
                if abs(p_lim):
                    # if not DISABLED:
                    # time.sleep(1.5)
                    p_control_frame.toggle_enable(force = 0, disable = 1)
                    gui_print('disabling motor')
                    DISABLED = True
                    ZERO_SEQ += 1
                    GUI_STATE = 1
            elif ZERO_SEQ == 4:
                # if not ZERO_SENT:
                gui_print('zeroing encoder')
                ser.write(bytes('z;p'.encode('utf-8')))
                p_pos_true = p_direction_param*p_datum_offset
                # ZERO_SENT = True
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 5:
                # if DISABLED and SET_ENABLE:
                gui_print('enabling motor')
                # ACK = None
                p_control_frame.toggle_enable(disable=0)
                # SET_ENABLE = False
                # MOVE_TO_DATUM = True
                MOVE_NUM = 1
                ZERO_SEQ += 1
                GUI_STATE = 1
            elif ZERO_SEQ == 6:
                if MOVE_NUM == 1:
                    ACK = None
                    gui_print('moving to datum 1')
                    move('p', 1, to_datum = True)
                    GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if SET_MICROSTEP:
                        gui_print('setting move2 uS')
                        set_microstep('p', move2_microsteps)
                        X_MICROSTEP_SET = True
                        GUI_STATE = 1
                    else:
                        gui_print('moving to datum 2')
                        move('p', 2, to_datum = True)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    gui_print('resetting params for next zero')
                    MOTOR_MASK = clearBit(MOTOR_MASK,0)
                    MOVE_NUM = 1
                    ZERO_SEQ = 1
                    SET_MICROSTEP = True
        else:
            GUI_STATE = 0
            EXECUTING = False
            # SET_MICROSTEP = True
            # ZEROING = False
            # DISABLED = False
            # ZERO_SENT = False
        prev_GUI_STATE = 4

# Default Motion Parameters
x_direction_param = -1 # 1 or -1 for direction sign change
z_direction_param = 1
lin_init_speed_param = 50 # Hz
lin_max_speed_param = 1500 # Hz
lin_accel_param = 50 # Hz/s

y_direction_param = 1
p_direction_param = 1
rot_init_speed_param = 50
rot_max_speed_param = 1500
rot_accel_param = 50

lin_motor_steps = 360/1.8 # 200 full steps per revolution
lin_Pitch = 1.5875
lin_enc_CPR = 4000

rot_motor_steps = 360/1.8 # 200 full steps per revolution
rot_gear_ratio = 72
rot_enc_CPR = 4000

move1_microsteps = 2
move2_microsteps = 256

lin_overshoot = 5 # steps
rot_overshoot = 1

# Default Instrument Parameters
x_datum_offset = 5 # mm
z_datum_offset = 50 # mm
y_datum_offset = 30 # deg
p_datum_offset = 30 # deg

lin_travel_range = 100 # mm
rot_travel_range = 60 # deg

def set_microstep(stage, microstep):
    if stage == 'x':
        uS_string = 't;x;' + str(microstep)
    elif stage == 'z':
        uS_string = 't;z;' + str(microstep)
    elif stage == 'y':
        uS_string = 't;y;' + str(microstep)
    elif stage == 'p':
        uS_string = 't;p;' + str(microstep)
    gui_print(uS_string)
    ser.write(bytes(uS_string.encode('utf-8')))

def move(stage, move, zero = False, to_datum = False):
    global x_target, z_target, y_target, p_target, x_pos_true, z_pos_true, y_pos_true, p_pos_true
    global x_dir, z_dir, y_dir, p_dir
    global x_direction_param, z_direction_param, y_direction_param, p_direction_param
    global lin_init_speed_param, lin_max_speed_param, lin_accel_param, lin_motor_steps, lin_Pitch
    global rot_init_speed_param, rot_max_speed_param, rot_accel_param, rot_motor_steps, rot_gear_ratio
    global move1_microsteps, move2_microsteps, lin_overshoot, rot_overshoot
    global lin_travel_range, rot_travel_range
    if move == 1:
        if stage == 'x':
            if zero:
                x_dir = -x_direction_param
                steps = round(move1_microsteps*lin_travel_range*lin_motor_steps/lin_Pitch) + 20*lin_overshoot
                move_string = 'm;x;'+ str(steps)+';'+str(x_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
            elif to_datum:
                x_dir = x_direction_param
                steps = round(move1_microsteps*abs(0-x_pos_true)*lin_motor_steps/lin_Pitch) + lin_overshoot
                move_string = 'm;x;'+ str(steps)+';'+str(x_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
            else:
                # print('move1')
                # print(x_target)
                # print(x_pos_true)
                if (x_target > x_pos_true):
                    x_dir = x_direction_param
                    steps = round(move1_microsteps*abs(x_target-x_pos_true)*lin_motor_steps/lin_Pitch) + lin_overshoot
                    move_string = 'm;x;'+ str(steps)+';'+str(x_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
                else:
                    x_dir = -x_direction_param
                    steps = round(move1_microsteps*abs(x_target-x_pos_true)*lin_motor_steps/lin_Pitch) - lin_overshoot
                    move_string = 'm;x;'+ str(steps)+';'+str(x_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
        if stage == 'z':
            if (z_target > z_pos_true):
                z_dir = z_direction_param
                steps = round(move1_microsteps*abs(z_target-z_pos_true)*lin_motor_steps/lin_Pitch) + lin_overshoot
                move_string = 'm;z;'+ str(steps)+';'+str(z_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
            else:
                z_dir = -z_direction_param
                steps = round(move1_microsteps*abs(z_target-z_pos_true)*lin_motor_steps/lin_Pitch) - lin_overshoot
                move_string = 'm;z;'+ str(steps)+';'+str(z_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
        if stage == 'y':
            # print('move1')
            # print(y_target)
            # print(y_pos_true)
            if (y_target > y_pos_true):
                y_dir = y_direction_param
                steps = round(move1_microsteps*abs(y_target-y_pos_true)*rot_motor_steps*rot_gear_ratio/360) + rot_overshoot
                move_string = 'm;y;'+ str(steps)+';'+str(y_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
            else:
                y_dir = -y_direction_param
                steps = round(move1_microsteps*abs(y_target-y_pos_true)*rot_motor_steps*rot_gear_ratio/360) - rot_overshoot
                move_string = 'm;y;'+ str(steps)+';'+str(y_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
        if stage == 'p':
            if (p_target > p_pos_true):
                p_dir = p_direction_param
                steps = round(move1_microsteps*abs(p_target-p_pos_true)*rot_motor_steps*rot_gear_ratio/360) + rot_overshoot
                move_string = 'm;p;'+ str(steps)+';'+str(p_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
            else:
                p_dir = -p_direction_param
                steps = round(move1_microsteps*abs(p_target-p_pos_true)*rot_motor_steps*rot_gear_ratio/360) - rot_overshoot
                move_string = 'm;p;'+ str(steps)+';'+str(p_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
    elif move == 2:
        if stage == 'x':
            if to_datum:
                gui_print('datum2')
                # print(0)
                print(x_pos_true)
                x_dir = -x_direction_param
                steps = round(move2_microsteps*abs(0-x_pos_true)*lin_motor_steps/lin_Pitch)
                move_string = 'm;x;'+ str(steps)+';'+str(x_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
            else:
                # print('move2')
                # print(x_target)
                # print(x_pos_true)
                if (x_target > x_pos_true):
                    x_dir = x_direction_param
                    steps = round(move2_microsteps*abs(x_target-x_pos_true)*lin_motor_steps/lin_Pitch)
                    move_string = 'm;x;'+ str(steps)+';'+str(x_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
                else:
                    x_dir = -x_direction_param
                    steps = round(move2_microsteps*abs(x_target-x_pos_true)*lin_motor_steps/lin_Pitch)
                    move_string = 'm;x;'+ str(steps)+';'+str(x_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
        if stage == 'z':
            if (z_target > z_pos_true):
                z_dir = z_direction_param
                steps = round(move2_microsteps*abs(z_target-z_pos_true)*lin_motor_steps/lin_Pitch)
                move_string = 'm;z;'+ str(steps)+';'+str(z_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
            else:
                z_dir = -z_direction_param
                steps = round(move2_microsteps*abs(z_target-z_pos_true)*lin_motor_steps/lin_Pitch)
                move_string = 'm;z;'+ str(steps)+';'+str(z_dir)+';'+str(lin_init_speed_param)+';'+str(lin_max_speed_param)+';'+str(lin_accel_param)
        if stage == 'y':
            # print('move2')
            # print(y_target)
            # print(y_pos_true)
            if (y_target > y_pos_true):
                y_dir = y_direction_param
                steps = round(move2_microsteps*abs(y_target-y_pos_true)*rot_motor_steps*rot_gear_ratio/360)
                move_string = 'm;y;'+ str(steps)+';'+str(y_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
            else:
                y_dir = -y_direction_param
                steps = round(move2_microsteps*abs(y_target-y_pos_true)*rot_motor_steps*rot_gear_ratio/360)
                move_string = 'm;y;'+ str(steps)+';'+str(y_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
        if stage == 'p':
            if (p_target > p_pos_true):
                p_dir = p_direction_param
                steps = round(move2_microsteps*abs(p_target-p_pos_true)*rot_motor_steps*rot_gear_ratio/360)
                move_string = 'm;p;'+ str(steps)+';'+str(p_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
            else:
                p_dir = -p_direction_param
                steps = round(move2_microsteps*abs(p_target-p_pos_true)*rot_motor_steps*rot_gear_ratio/360)
                move_string = 'm;p;'+ str(steps)+';'+str(p_dir)+';'+str(rot_init_speed_param)+';'+str(rot_max_speed_param)+';'+str(rot_accel_param)
    else:
        gui_print('Move command failed')
        return
    gui_print(move_string)
    ser.write(bytes(move_string.encode('utf-8')))

# Credit to: https://wiki.python.org/moin/BitManipulation
def testBit(int_type, offset):
    mask = 1 << offset
    return(int_type & mask)

# Credit to: https://wiki.python.org/moin/BitManipulation
def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)

# Credit to: https://wiki.python.org/moin/BitManipulation
def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)

# def move_pitch():
#     messagebox.showinfo("Control","move pitch")

def move_instrument():
    messagebox.showinfo("Control","move Instrument")

def update_status(status):
    global x_pos, z_pos, y_pos, p_pos, prev_x_pos, prev_z_pos, prev_y_pos, prev_p_pos
    global x_lim, z_lim, y_lim, p_lim, x_speed, z_speed, y_speed, p_speed
    global X_STOPPED
    global lin_Pitch, lin_enc_CPR, rot_gear_ratio, rot_enc_CPR
    global x_direction_param, z_direction_param, y_direction_param, p_direction_param
    x_pos = x_direction_param*float(status[0])*lin_Pitch/lin_enc_CPR  # convert to deg
    z_pos = z_direction_param*float(status[1])*lin_Pitch/lin_enc_CPR
    y_pos = y_direction_param*float(status[2])*360/(rot_enc_CPR*rot_gear_ratio)
    p_pos = p_direction_param*float(status[3])*360/(rot_enc_CPR*rot_gear_ratio)
    if abs(x_pos-prev_x_pos) <= 0.02:
        X_STOPPED = True
    else:
        X_STOPPED = False
    x_lim = float(status[4])
    z_lim = float(status[5])
    y_lim = float(status[6])
    p_lim = float(status[7])
    x_speed = 1000*(x_pos - prev_x_pos)/(50)
    z_speed = 1000*(z_pos - prev_z_pos)/(50)
    y_speed = 1000*(y_pos - prev_y_pos)/(50)  # convert to deg/s where 100 is hub task period in ms
    p_speed = 1000*(p_pos - prev_p_pos)/(50)
    prev_x_pos = x_pos
    prev_z_pos = z_pos
    prev_y_pos = y_pos
    prev_p_pos = p_pos
    x_status_frame.update_position("{0:.4f}".format(x_pos)) # convert to deg
    z_status_frame.update_position("{0:.4f}".format(z_pos))
    y_status_frame.update_position("{0:.4f}".format(y_pos))
    p_status_frame.update_position("{0:.4f}".format(p_pos))
    x_status_frame.update_speed("{0:.2f}".format(x_speed))
    z_status_frame.update_speed("{0:.2f}".format(z_speed))
    y_status_frame.update_speed("{0:.2f}".format(y_speed))
    p_status_frame.update_speed("{0:.2f}".format(p_speed))
    if x_lim <0:
        x_status_frame.limit_on('m')
    elif x_lim >0:
        x_status_frame.limit_on('p')
    else:
        x_status_frame.limit_off('p')
        x_status_frame.limit_off('m')
    if z_lim <0:
        z_status_frame.limit_on('m')
    elif z_lim >0:
        z_status_frame.limit_on('p')
    else:
        z_status_frame.limit_off('p')
        z_status_frame.limit_off('m')
    if y_lim <0:
        y_status_frame.limit_on('m')
    elif y_lim >0:
        y_status_frame.limit_on('p')
    else:
        y_status_frame.limit_off('p')
        y_status_frame.limit_off('m')
    if p_lim <0:
        p_status_frame.limit_on('m')
    elif p_lim >0:
        p_status_frame.limit_on('p')
    else:
        p_status_frame.limit_off('p')
        p_status_frame.limit_off('m')

prev_string = ''
def log_print(to_print, stamp = True):
    global prev_string, timestamp
    if to_print != prev_string:
        if stamp:
            log.insert(END, str(int(time.time()*1000 - timestamp))+ ' ')
            log.insert(END, to_print)
        else:
            log.insert(END, to_print)
    prev_string = to_print

def gui_print(to_print, stamp = True):
    global timestamp
    if stamp:
        gui_printer.insert(END, str(int(time.time()*1000 - timestamp))+ ' ')
        gui_printer.insert(END, to_print)
        gui_printer.insert(END, '\n')
    else:
        gui_printer.insert(END, to_print)
        gui_printer.insert(END, '\n')


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- GUI Window ------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
window = Tk()
window.title("MUVI Manipulator User Interface")
window.configure(background='white')
window.geometry("1250x950")

# Top Row
cal_poly_logo = PhotoImage(file = "cal_poly_me_logo.gif")
Label (window, image=cal_poly_logo, bg="white") .grid(row=0, column = 0, sticky = 'W')

Label(window, text="4 DOF \n Manipulator Interface", bg='white',font=(None, 15, 'bold')).grid(row=0,column=3)

ucb_logo = PhotoImage(file = "SSL-Berkeley-80blue.gif")
Label (window, image=ucb_logo, bg="white") .grid(row=0, column = 5, sticky = 'E')

# Status Row
status_frame = LabelFrame(window, text="Status Panel", bg='white')
status_frame.grid(row=3, column=0, rowspan=1, columnspan=50, sticky='WE', padx=5, pady=5)

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

x_status_frame.update_mark()
z_status_frame.update_mark()
y_status_frame.update_mark()
p_status_frame.update_mark()

# x_status_frame.limit_on('p')

# Control Row
control_frame = LabelFrame(window, text="Control Panel", bg='white')
control_frame.grid(row=8, column=0, rowspan=1, columnspan=50, sticky='WE', padx=5, pady=5)

Button(control_frame, text ="STOP", command = stop_manipulator, bg="red3", height=2, width=20).grid(row=1,column=0, sticky='W', padx=10, pady=5)

cmd_label = Label(control_frame, text="Send Command:", bg='white').grid(row=1,column=3, sticky=E)
cmd = Entry(control_frame, width = 25, bg="white", justify='right')
cmd.grid(row=1, column=4, columnspan = 4, sticky=W)
cmd.insert(0,'m;p;1000;1;50;6000;50')
# cmd.insert(0,'d;p')

Button(control_frame, text ="Send", command = send_cmd, height=2, width=20).grid(row=1,column=9, sticky='W', padx=10, pady=5)

Button(control_frame, text ="Reset System", command = reset, height=2, width=20).grid(row=9,column=9, columnspan = 1, sticky='W', padx=10, pady=5)

Button(control_frame, text= "Move Stages", height=2, width=20, command=move_stages).grid(row=9, column=0, sticky=W, padx=10, pady=5)

Button(control_frame, text= "Enable All", height=2, width=20, command=enable_all).grid(row=9, column=3, sticky=W, padx=10, pady=5)

Button(control_frame, text= "Zero All", height=2, width=20, command=zero_all).grid(row=9, column=6, sticky=W, padx=10, pady=5)

# Button(control_frame, text= "Load Motion Parameters", height=2, width=20, command=set_motion_params).grid(row=9, column=9, sticky=W, padx=10, pady=5)

x_control_frame = control_box(control_frame, 10, 0, "mm", "X Translation", x_status_frame, 'x')
z_control_frame = control_box(control_frame, 10, 3, "mm", "Z Translation", z_status_frame, 'z')
y_control_frame = control_box(control_frame, 10, 6, "deg", "Yaw Rotation", y_status_frame, 'y')
p_control_frame = control_box(control_frame, 10, 9, "deg", "Pitch Rotation", p_status_frame, 'p')

x_control_frame.update_target('0.0000')
z_control_frame.update_target('0.0000')
y_control_frame.update_target('0.0000')
p_control_frame.update_target('0.0000')

x_control_frame.set_jogsize('0.0000')
z_control_frame.set_jogsize('0.0000')
y_control_frame.set_jogsize('0.0000')
p_control_frame.set_jogsize('0.0000')

# Run Test Row
test_frame = LabelFrame(window, text="Run Test", bg='white')
test_frame.grid(row=9, column=0, columnspan=50, sticky='WE', padx=5, pady=5)

Button(test_frame, text= "Load Motion Parameters", height=2, width=20, command=set_motion_params).grid(row=26, column=1, columnspan = 3, sticky=W, padx=5, pady=3)

config_label = Label(test_frame, text="Config File:", bg='white').grid(row=26,column=7, sticky=E, padx=10, pady=5)
config = Entry(test_frame, width = 45, bg="white", justify='right')
config.grid(row=26, column=8, columnspan = 3, sticky=W)

Button(test_frame, text= "Load Config File", height=2, width=20, command=browse_button).grid(row=26, column=4, columnspan = 3, sticky=W, padx=5, pady=3)

Button(test_frame, text= "FOV Sweep", height=2, width=20, command=FOV_sweep).grid(row=27, column=1, columnspan = 3, sticky=W, padx=5, pady=3)

Button(test_frame, text= "Boresight", height=2, width=20, command=boresight).grid(row=27, column=4, columnspan = 3, sticky=W, padx=5, pady=3)

Button(test_frame, text= "Stray Light Sweep", height=2, width=20, command=SL_sweep).grid(row=27, column=7, columnspan = 3, sticky=W, padx=5, pady=3)

pitch_label = Label(test_frame, text="Pitch (\u03B8):", bg='white').grid(row=28,column=1, sticky=W, padx=5, pady=(10,3))
pitch = Entry(test_frame, width = 14, bg="white", justify='right')
pitch.grid(row=28, column=2, columnspan = 1, sticky=W, pady=(10,3))
pitch_units = Label(test_frame, text="deg", bg='white').grid(row=28,column=3, sticky=W, pady=(10,3))

pitch.insert(0,'0.0000')
# Button(test_frame, text= "Move Pitch", width=20, command=move_pitch).grid(row=29, column=1, columnspan = 3, sticky=W, padx=5, pady=3)

yaw_label = Label(test_frame, text="Yaw (\u03C8):", bg='white').grid(row=28,column=4, sticky=W, padx=5, pady=(10,3))
yaw = Entry(test_frame, width = 14, bg="white", justify='right')
yaw.grid(row=28, column=5, columnspan = 1, sticky=W, pady=(10,3))
yaw_units = Label(test_frame, text="deg", bg='white').grid(row=28,column=6, sticky=W, pady=(10,3))

yaw.insert(0,'0.0000')

Button(test_frame, text= "Move Instrument", width=20, command=move_instrument).grid(row=29, column=1, columnspan = 3, sticky=W, padx=5, pady=3)

Label(window, text="Created by: Jason Grillo \n Cal Poly Mechanical Engineering \n In Collaboration with UCB Space Sciences Laboratories \n \u00A9 2019, All Rights Reserved", bg='white',font=(None, 10)).grid(row=10,column=3)


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- Run the GUI -----------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

# Credit to: https://robotic-controls.com/learn/python-guis/tkinter-serial

log_label = Label(window, text="Manipulator Log", bg='white').grid(row=0,column=61, sticky=SE, padx=(0,80))
log = Text (window, width=55, height=33, takefocus=0, bg='white')
log.grid(row=1,rowspan=10, column = 60, columnspan = 3, sticky = NE, padx=5, pady=13)

gui_printer_label = Label(window, text="GUI Log", bg='white').grid(row=8,column=61, sticky=SE, padx=(0,100))
gui_printer = Text (window, width=55, height=10, takefocus=0, bg='white')
gui_printer.grid(row=9,rowspan=20, column = 60, columnspan = 3, sticky = NE, padx=5, pady=13)

timestamp = time.time() * 1000
log_print('|Timestamp (ms)|\tFeedback|\n', stamp = False)
gui_print('|Timestamp (ms)|\tFeedback|', stamp = False)

# serialPort = "COM6"
serialPort = "COM7"
baudRate = 115200
try:
    ser = serial.Serial(serialPort , baudRate, timeout=0, writeTimeout=0,dsrdtr=True) #ensure non-blocking
    ser.setDTR(True)
    ser.flush()
    ser.write(b'r;r') # reset the microcontroller

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
            GUI_state_machine()
            # update_status(serBuffer)
            # log_print(serBuffer)
            # log.insert(END, serBuffer)
            # log.insert('0.0', serBuffer)
            serBuffer = "" # empty the buffer
        else:
            serBuffer += c # add to the buffer
    window.after(10, readSerial) # check serial again soon

# after initializing serial, a microcontroller may need a bit of time to reset
window.after(100, readSerial)

window.mainloop()
