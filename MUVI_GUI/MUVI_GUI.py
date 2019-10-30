# import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
# from PIL import Image, ImageTk
import serial
import time
import csv

import NLS4
import RM5
import manipulator

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -------------------------- Global Variables ---------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

config_file = None
serBuffer = ""

x_target = 0.0
z_target = 0.0
y_target = 0.0
p_target = 0.0

x_jog = 0.0
z_jog = 0.0
y_jog = 0.0
p_jog = 0.0

GUI_STATE = 0
prev_GUI_STATE = 0
MOTOR_MASK = 0b0000  # x;z;y;p
ACK = None
EXECUTING = False
MOVE_NUM = 1
ZERO_SEQ = 1

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -------------------------- Class Definitions --------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

class CSV_Read():
    def __init__(self, filename):
        with open(filename, "r") as f_input:
            csv_input = csv.reader(f_input)
            self.details = list(csv_input)
        f_input.close()

    def get_col_row(self, col, row):
        return self.details[row-1][col-1]

class status_box():
    def __init__(self,frame, row, column, units, name):
        self.row = row
        self.column = column
        self.units = units
        self.name = name

        self.status_frame = LabelFrame(frame, text=self.name, bg='white')
        self.status_frame.grid(row=self.row, column=self.column, rowspan=3, columnspan=3, sticky='WE', padx=5, pady=5)

        self.pos_label = Label(self.status_frame, text="Position:", bg='white').grid(row=self.row,column=self.column, sticky=W, padx=5, pady=1)
        self.position = Entry(self.status_frame, width = 10, bg='gray80', justify='right')
        self.position.grid(row=self.row, column=self.column+1, sticky=E)
        self.pos_units = Label(self.status_frame, text=self.units, bg='white').grid(row=self.row,column=self.column+2, sticky=W)

        self.speed_label = Label(self.status_frame, text="Speed:", bg='white').grid(row=(self.row+1),column=self.column, sticky=W, padx=5, pady=1)
        self.speed = Entry(self.status_frame, width = 10, bg='gray80', justify='right')
        self.speed.grid(row=(self.row+1), column=self.column+1, sticky=E)
        self.speed_units = Label(self.status_frame, text=(self.units+"/s"), bg='white').grid(row=(self.row+1),column=self.column+2, sticky=W)

        self.mark_label = Label(self.status_frame, text="Mark:", bg='white').grid(row=(self.row+2),column=self.column, sticky=W, padx=5, pady=1)
        self.mark = Entry(self.status_frame, width = 10, bg='gray80',  justify='right')
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

        self.mark_mark = Button(self.status_frame, text="Mark Position", width=15, command=self.mark_mark, bg='light blue')
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
        self.enable_mot = Button(self.control_frame, text="OFF", width=8, command=self.toggle_enable, bg='red3')
        self.enable_mot.grid(row=self.row, column=self.column+1, sticky=E, pady=2)

        self.targ_label = Label(self.control_frame, text="Target:", bg='white').grid(row=self.row+1,column=self.column, sticky=W, padx=5, pady=1)
        self.target = Entry(self.control_frame, width = 10, bg="white", justify='right')
        self.target.grid(row=self.row+1, column=self.column+1, sticky=E)
        self.targ_units = Label(self.control_frame, text=self.units, bg='white').grid(row=self.row+1,column=self.column+2,columnspan=2, sticky=W)

        self.jog_label = Label(self.control_frame, text="Jog Size:", bg='white').grid(row=(self.row+2),column=self.column, sticky=W, padx=5, pady=1)
        self.jog_size = Entry(self.control_frame, width = 10, bg="white", justify='right')
        self.jog_size.grid(row=(self.row+2), column=self.column+1, sticky=E)
        self.jog_units = Label(self.control_frame, text=(self.units), bg='white').grid(row=(self.row+2),column=self.column+2,columnspan=2,  sticky=W)

        self.jog_m = Button(self.control_frame, text="Jog -", width=5, command=self.jog_m, bg='light blue')
        self.jog_m.grid(row=self.row+3, column=self.column, sticky=W, padx=(20,0), pady=3)

        self.jog_p = Button(self.control_frame, text="Jog +", width=5, command=self.jog_p, bg='light blue')
        self.jog_p.grid(row=self.row+3, column=self.column+1, sticky=W, padx=(25,0), pady=3)

        self.set_mark_to_targ = Button(self.control_frame, text="Put Mark to Target", width=15, command=self.set_mark_to_targ, bg='light blue')
        self.set_mark_to_targ.grid(row=self.row+4, column=self.column,columnspan=4, sticky=W, padx=20, pady=3)

        self.mark_datum = Button(self.control_frame, text= "Set New Datum", width=15, command=self.mark_datum, bg='light blue')
        self.mark_datum.grid(row=self.row+5, column=self.column,columnspan=4, sticky=W, padx=20, pady=3)

    def toggle_enable(self, force = 1, disable = 1, send_cmd = True):
        # https://www.daniweb.com/programming/software-development/code/429838/simple-tkinter-toggle-button
        '''
        use
        t_btn.config('text')[-1]
        to get the present state of the toggle button
        '''
        if (self.enable_mot.config('text')[-1] == 'ON' or not force) and disable:
            if send_cmd:
                toggle_string = 'd;' + self.stage.get_name()
                ser.write(bytes(toggle_string.encode('utf-8')))
            self.enable_mot.config(text='OFF', bg = 'red3')
            self.stage.set_enable(False)
            self.stage.set_enable_time(time.time())
            self.ENABLED = 0
        else:
            if send_cmd:
                toggle_string = 'e;' + self.stage.get_name()
                ser.write(bytes(toggle_string.encode('utf-8')))
            self.enable_mot.config(text='ON', bg = 'lime green')
            self.stage.set_enable(True)
            self.stage.set_enable_time(time.time())
            self.ENABLED = 1

    def jog_m(self):
        try:
            self.TARGET -= float(self.jog_size.get())
        except:
            gui_print('Must enter number to target')
        self.update_target(round(self.TARGET,4))

    def jog_p(self):
        try:
            self.TARGET += float(self.jog_size.get())
        except:
            gui_print('Must enter number to target')
        self.update_target(round(self.TARGET,4))

    def set_mark_to_targ(self):
        self.target.delete(0, END)
        self.target.insert(0, self.status_box.mark.get())

    def mark_datum(self):
        self.target.delete(0, END)
        self.target.insert(0, '0')
        self.stage.new_datum()

    def update_target(self, new_target):
        self.target.delete(0, END)
        self.target.insert(0, str(new_target))

    def get_target(self):
        return float(self.target.get())

    def set_jogsize(self, new_jogsize):
        self.jog_size.delete(0, END)
        self.jog_size.insert(0, str(new_jogsize))

    def get_enable(self):
        return self.stage.get_status()[0]

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- Methods ---------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

def stop_manipulator():
    write_string_to_ser('a;a')
    x_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    z_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    y_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    p_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    reset_params()
    gui_print('Manipulator stopped by User.')

def set_motion_params():
    global x_stage, z_stage, y_stage, p_stage
    global motion_filename, motion_params
    motion_filename = filedialog.askopenfilename(initialdir = "E:\MUVI\Manipulator\Code_Repository\thesis-manipulator\MUVI_GUI",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
    motion_params = CSV_Read(motion_filename)
    stages = [x_stage, z_stage, y_stage, p_stage]
    param = 1
    start = 1
    for stage in stages:
        param_list = []
        for index in range(11):
            param_list.append(motion_params.get_col_row(param,2))
            param += 4
        param_list.append(motion_params.get_col_row(45,2))
        stage.set_motion_params(param_list)
        start += 1
        param = start
    gui_print('Motion Parameters Loaded.')

def set_instr_params():
    global x_stage, z_stage, y_stage, p_stage
    global MUVI
    global instrument_filename, instrument_params
    instrument_filename = filedialog.askopenfilename(initialdir = "E:\MUVI\Manipulator\Code_Repository\thesis-manipulator\MUVI_GUI",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
    instrument_params = CSV_Read(instrument_filename)
    config.delete(0, END)
    config.insert(0,str(instrument_filename))
    stages = [x_stage, z_stage, y_stage, p_stage]
    param = 1
    start = 1
    for stage in stages:
        param_list = []
        for index in range(2):
            param_list.append(instrument_params.get_col_row(param,2))
            param += 4
        stage.set_instrument_params(param_list)
        start += 1
        param = start
    stage.set_instrument_params(param_list)
    param_list = [instrument_params.get_col_row(9,2), instrument_params.get_col_row(10,2)]
    param = 11
    for index in range(8):
        quat_list = []
        for quaternion in range(4):
            quat_list.append(instrument_params.get_col_row(param,quaternion+2))
        param_list.append(quat_list)
        param += 1
    MUVI.set_instrument_params(param_list)
    gui_print('Instrument Parameters Loaded.')

def move_stages():
    global MOTOR_MASK, GUI_STATE, EXECUTING, MOVE_NUM
    global x_stage, z_stage, y_stage, p_stage
    global x_target, z_target, y_target, p_target
    if not EXECUTING:
        x_target = x_control_frame.get_target()
        z_target = z_control_frame.get_target()
        y_target = y_control_frame.get_target()
        p_target = p_control_frame.get_target()
        if not x_stage.get_true_position() == x_target and x_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,3)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,3)
        if not z_stage.get_true_position() == z_target and z_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,2)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,2)
        if not y_stage.get_true_position() == y_target and y_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,1)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,1)
        if not p_stage.get_true_position() == p_target and p_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,0)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,0)
        MOVE_NUM = 1
        GUI_STATE = 3
        EXECUTING = True
        gui_print('Moving Stages: '+ 'x '+ str(x_target) + '; z '+ str(z_target) +'; \u03B8 ' + str(p_target)+ '; \u03C8 ' + str(y_target))
    else:
        return

def move_instrument():
    global MOTOR_MASK, GUI_STATE, EXECUTING, MOVE_NUM
    global x_target, z_target, y_target, p_target
    x_target, z_target, y_target, p_target = MUVI.get_point_targets(float(pitch.get()), float(yaw.get()))
    if not EXECUTING:
        if not x_stage.get_true_position() == x_target and x_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,3)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,3)
        if not z_stage.get_true_position() == z_target and z_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,2)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,2)
        if not y_stage.get_true_position() == y_target and y_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,1)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,1)
        if not p_stage.get_true_position() == p_target and p_control_frame.get_enable():
            MOTOR_MASK = setBit(MOTOR_MASK,0)
        else:
            MOTOR_MASK = clearBit(MOTOR_MASK,0)
        MOVE_NUM = 1
        GUI_STATE = 3
        EXECUTING = True
        x_control_frame.update_target(str(x_target))
        z_control_frame.update_target(str(z_target))
        y_control_frame.update_target(str(y_target))
        p_control_frame.update_target(str(p_target))
        gui_print('Moving Instrument: '+ 'x '+ str(x_target) + '; z '+ str(z_target) +'; \u03B8 ' + str(p_target)+ '; \u03C8 ' + str(y_target))
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
    global MOTOR_MASK, GUI_STATE, EXECUTING, ZERO_SEQ
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
        gui_print('Zeroing Stages')
    else:
        return

def FOV_sweep():
    messagebox.showinfo("Run Test","Sweeping FOV")

def boresight():
    messagebox.showinfo("Run Test","Boresight")

def SL_sweep():
    messagebox.showinfo("Run Test","Sweeping Stray Light")

def take_picture():
    messagebox.showinfo("Run Test","Capture Image")

def send_cmd():
    write_string_to_ser(cmd.get())
    gui_print('Command sent.')

def reset_params():
    global x_stage, z_stage, y_stage, p_stage
    global x_target, z_target, y_target, p_target
    global GUI_STATE, prev_GUI_STATE, MOTOR_MASK, ACK, EXECUTING, MOVE_NUM, ZERO_SEQ
    x_target = 0.0
    z_target = 0.0
    y_target = 0.0
    p_target = 0.0
    GUI_STATE = 0
    prev_GUI_STATE = 0
    MOTOR_MASK = 0b0000  # x;z;y;p
    ACK = None
    EXECUTING = False
    MOVE_NUM = 1
    ZERO_SEQ = 1

def reset():
    global x_stage, z_stage, y_stage, p_stage
    global x_target, z_target, y_target, p_target
    write_string_to_ser('r;a')
    x_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    z_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    y_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    p_control_frame.toggle_enable(force = 0, disable = 1, send_cmd = False)
    reset_params()
    x_control_frame.update_target('0.0000')
    z_control_frame.update_target('0.0000')
    y_control_frame.update_target('0.0000')
    p_control_frame.update_target('0.0000')
    # x_control_frame.set_jogsize('0.0000')
    # z_control_frame.set_jogsize('0.0000')
    # y_control_frame.set_jogsize('0.0000')
    # p_control_frame.set_jogsize('0.0000')
    x_target = 0.0
    z_target = 0.0
    y_target = 0.0
    p_target = 0.0
    x_stage.reset()
    z_stage.reset()
    y_stage.reset()
    p_stage.reset()


def read_data():
    global serBuffer, MOVE_NUM, ACK
    global x_stage, z_stage, y_stage, p_stage
    log_print(serBuffer)
    uC_resp = serBuffer[:-1:] # remove last character (/n)
    uC_resp = uC_resp.split(';')
    if not (' ' in uC_resp[0]):
        # filter out non-acknowledge data
        if not uC_resp[0].isalpha() and len(uC_resp)>1:
            return uC_resp
        else:
            ACK = uC_resp[0]
            if ACK == 's':
                if uC_resp[1] == 'x':
                    x_stage.set_moving(False)
                    if MOVE_NUM == 1:
                        x_stage.set_step_pos(uC_resp[2],1)
                    elif MOVE_NUM == 2:
                        x_stage.set_step_pos(uC_resp[2],2)
                elif uC_resp[1] == 'z':
                    z_stage.set_moving(False)
                    if MOVE_NUM == 1:
                        z_stage.set_step_pos(uC_resp[2],1)
                    elif MOVE_NUM == 2:
                        z_stage.set_step_pos(uC_resp[2],2)
                elif uC_resp[1] == 'y':
                    y_stage.set_moving(False)
                    if MOVE_NUM == 1:
                        y_stage.set_step_pos(uC_resp[2],1)
                    elif MOVE_NUM == 2:
                        y_stage.set_step_pos(uC_resp[2],2)
                elif uC_resp[1] == 'p':
                    p_stage.set_moving(False)
                    if MOVE_NUM == 1:
                        p_stage.set_step_pos(uC_resp[2],1)
                    elif MOVE_NUM == 2:
                        p_stage.set_step_pos(uC_resp[2],2)
            elif ACK == 't':
                if uC_resp[1] == 'x':
                    if float(uC_resp[2]) == x_stage.get_move1_uS():
                        x_stage.set_microstep(False)
                    elif float(uC_resp[2]) == x_stage.get_move2_uS():
                        x_stage.set_microstep(True)
                elif uC_resp[1] == 'z':
                    if float(uC_resp[2]) == z_stage.get_move1_uS():
                        z_stage.set_microstep(False)
                    elif float(uC_resp[2]) == z_stage.get_move2_uS():
                        z_stage.set_microstep(True)
                elif uC_resp[1] == 'y':
                    if float(uC_resp[2]) == y_stage.get_move1_uS():
                        y_stage.set_microstep(False)
                    elif float(uC_resp[2]) == y_stage.get_move2_uS():
                        y_stage.set_microstep(True)
                elif uC_resp[1] == 'p':
                    if float(uC_resp[2]) == p_stage.get_move1_uS():
                        p_stage.set_microstep(False)
                    elif float(uC_resp[2]) == p_stage.get_move2_uS():
                        p_stage.set_microstep(True)
            elif ACK == 'm':
                if uC_resp[1] == 'x':
                    x_stage.set_moving(True)
                elif uC_resp[1] == 'z':
                    z_stage.set_moving(True)
                elif uC_resp[1] == 'y':
                    y_stage.set_moving(True)
                elif uC_resp[1] == 'p':
                    p_stage.set_moving(True)
            elif ACK == 'e':
                if uC_resp[1] == 'x':
                    x_stage.set_enable(True)
                elif uC_resp[1] == 'z':
                    z_stage.set_enable(True)
                elif uC_resp[1] == 'y':
                    y_stage.set_enable(True)
                elif uC_resp[1] == 'p':
                    p_stage.set_enable(True)
            elif ACK == 'd':
                if uC_resp[1] == 'x':
                    x_stage.set_enable(False)
                elif uC_resp[1] == 'z':
                    z_stage.set_enable(False)
                elif uC_resp[1] == 'y':
                    y_stage.set_enable(False)
                elif uC_resp[1] == 'p':
                    p_stage.set_enable(False)
            elif ACK == 'z':
                if uC_resp[1] == 'x':
                    x_stage.set_zeroed(True)
                elif uC_resp[1] == 'z':
                    z_stage.set_zeroed(True)
                elif uC_resp[1] == 'y':
                    y_stage.set_zeroed(True)
                elif uC_resp[1] == 'p':
                    p_stage.set_zeroed(True)
            return None

def GUI_state_machine():
    global GUI_STATE, prev_GUI_STATE, MOTOR_MASK, ACK, EXECUTING, MOVE_NUM, ZERO_SEQ, enable_time
    global x_stage, z_stage, y_stage, p_stage
    global x_target, z_target, y_target, p_target
    global x_datum_offset, z_datum_offset, y_datum_offset, p_datum_offset

    parsed = read_data()
    if parsed:
        update_status(parsed)

    # IDLE
    if GUI_STATE == 0:
        # because the x and z stages warm up quickly at idle, need to shut them off after 30 seconds when not moving them..
        if (time.time()-x_stage.get_enable_time()) > 30 and x_control_frame.get_enable():
            x_control_frame.toggle_enable(force = 0, disable = 1)
        if (time.time()-z_stage.get_enable_time()) > 30 and z_control_frame.get_enable():
            z_control_frame.toggle_enable(force = 0, disable = 1)
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
            # SET_MICROSTEP = True
            GUI_STATE = prev_GUI_STATE
            ACK = None
        elif ACK == 't':
            GUI_STATE = prev_GUI_STATE
            # SET_MICROSTEP = False
            ACK = None
        elif ACK == 'd':
            GUI_STATE = prev_GUI_STATE
            ACK = None
        elif ACK == 'z':
            GUI_STATE = prev_GUI_STATE
            ACK = None
        elif (time.time()-ACK_start) > 10 and not (x_stage.get_status()[1] or z_stage.get_status()[1] or y_stage.get_status()[1] or p_stage.get_status()[1]):
            # if there hasnt been an acknowledge in 5 seconds, send the cmd again, unless there's a stage moving..
            gui_print('acknowledge timeout')
            GUI_STATE = prev_GUI_STATE

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
            if x_stage.get_status()[0]:
                if MOVE_NUM == 1:
                    if x_stage.get_microstep():
                        send_microstep('x', x_stage.get_move1_uS())
                        GUI_STATE = 1
                    else:
                        move('x', 1)
                        GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if not x_stage.get_microstep():
                        send_microstep('x', x_stage.get_move2_uS())
                        GUI_STATE = 1
                    else:
                        move('x', 2)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    MOTOR_MASK = clearBit(MOTOR_MASK,3)
                    MOVE_NUM = 1
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,3)
                MOVE_NUM = 1
        elif testBit(MOTOR_MASK,2):
            if z_stage.get_status()[0]:
                if MOVE_NUM == 1:
                    if z_stage.get_microstep():
                        send_microstep('z', z_stage.get_move1_uS())
                        GUI_STATE = 1
                    else:
                        move('z', 1)
                        GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if not z_stage.get_microstep():
                        send_microstep('z', z_stage.get_move2_uS())
                        GUI_STATE = 1
                    else:
                        move('z', 2)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    MOTOR_MASK = clearBit(MOTOR_MASK,2)
                    MOVE_NUM = 1
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,2)
                MOVE_NUM = 1
        elif testBit(MOTOR_MASK,1):
            if y_stage.get_status()[0]:
                if MOVE_NUM == 1:
                    if y_stage.get_microstep():
                        send_microstep('y', y_stage.get_move1_uS())
                        GUI_STATE = 1
                    else:
                        move('y', 1)
                        GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if not y_stage.get_microstep():
                        send_microstep('y', y_stage.get_move2_uS())
                        GUI_STATE = 1
                    else:
                        move('y', 2)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    MOTOR_MASK = clearBit(MOTOR_MASK,1)
                    MOVE_NUM = 1
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,1)
                MOVE_NUM = 1
        elif testBit(MOTOR_MASK,0):
            if p_stage.get_status()[0]:
                if MOVE_NUM == 1:
                    if p_stage.get_microstep():
                        send_microstep('p', p_stage.get_move1_uS())
                        GUI_STATE = 1
                    else:
                        move('p', 1)
                        GUI_STATE = 1
                elif MOVE_NUM == 2:
                    if not p_stage.get_microstep():
                        send_microstep('p', p_stage.get_move2_uS())
                        GUI_STATE = 1
                    else:
                        move('p', 2)
                        GUI_STATE = 1
                elif MOVE_NUM == 3:
                    MOTOR_MASK = clearBit(MOTOR_MASK,0)
                    MOVE_NUM = 1
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,0)
                MOVE_NUM = 1
        else:
            GUI_STATE = 0
            EXECUTING = False
            gui_print('Finished moving stages.')
        prev_GUI_STATE = 3

    # ZEROING STAGES
    elif GUI_STATE == 4:
        if testBit(MOTOR_MASK,3):
            if x_stage.get_status()[0]:
                if ZERO_SEQ == 1:
                    if x_stage.get_microstep():
                        gui_print('... Setting coarse microsteps')
                        send_microstep('x', x_stage.get_move1_uS())
                        ZERO_SEQ += 1
                        GUI_STATE = 1
                    else:
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 2:
                    gui_print('... Finding negative hard stop')
                    move('x', 1, zero = True)
                    ZERO_SEQ += 1
                elif ZERO_SEQ == 3:
                    if abs(x_stage.get_limit()):
                        gui_print('... Hard stop reached')
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 4:
                    gui_print('... Zeroing encoder and updating current position')
                    write_string_to_ser('z;x')
                    x_stage.cal_step_pos()
                    MOVE_NUM = 1
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                elif ZERO_SEQ == 5:
                    if MOVE_NUM == 1:
                        ACK = None
                        gui_print('... Moving to DATUM with coarse microsteps')
                        move('x', 1, to_datum = True)
                        GUI_STATE = 1
                    elif MOVE_NUM == 2:
                        if not x_stage.get_microstep():
                            gui_print('... Setting fine microsteps')
                            send_microstep('x', x_stage.get_move2_uS())
                            GUI_STATE = 1
                        else:
                            gui_print('... Finishing move to DATUM with fine microsteps')
                            move('x', 2, to_datum = True)
                            GUI_STATE = 1
                    elif MOVE_NUM == 3:
                        MOTOR_MASK = clearBit(MOTOR_MASK,3)
                        MOVE_NUM = 1
                        ZERO_SEQ = 1
                        gui_print('... X Stage zeroing complete')
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,3)
                MOVE_NUM = 1
                ZERO_SEQ = 1
        elif testBit(MOTOR_MASK,2):
            if z_stage.get_status()[0]:
                if ZERO_SEQ == 1:
                    if z_stage.get_microstep():
                        gui_print('... Setting coarse microsteps')
                        send_microstep('z', z_stage.get_move1_uS())
                        ZERO_SEQ += 1
                        GUI_STATE = 1
                    else:
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 2:
                    gui_print('... Finding negative hard stop')
                    move('z', 1, zero = True)
                    ZERO_SEQ += 1
                elif ZERO_SEQ == 3:
                    if abs(z_stage.get_limit()):
                        gui_print('... Hard stop reached')
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 4:
                    gui_print('... Zeroing encoder and updating current position')
                    write_string_to_ser('z;z')
                    z_stage.cal_step_pos()
                    MOVE_NUM = 1
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                elif ZERO_SEQ == 5:
                    if MOVE_NUM == 1:
                        ACK = None
                        gui_print('... Moving to DATUM with coarse microsteps')
                        move('z', 1, to_datum = True)
                        GUI_STATE = 1
                    elif MOVE_NUM == 2:
                        if not z_stage.get_microstep():
                            gui_print('... Setting fine microsteps')
                            send_microstep('z', z_stage.get_move2_uS())
                            GUI_STATE = 1
                        else:
                            gui_print('... Finishing move to DATUM with fine microsteps')
                            move('z', 2, to_datum = True)
                            GUI_STATE = 1
                    elif MOVE_NUM == 3:
                        MOTOR_MASK = clearBit(MOTOR_MASK,2)
                        MOVE_NUM = 1
                        ZERO_SEQ = 1
                        gui_print('... Z Stage zeroing complete')
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,2)
                MOVE_NUM = 1
                ZERO_SEQ = 1
        elif testBit(MOTOR_MASK,1):
            if y_stage.get_status()[0]:
                if ZERO_SEQ == 1:
                    if y_stage.get_microstep():
                        gui_print('... Setting coarse microsteps')
                        send_microstep('y', y_stage.get_move1_uS())
                        ZERO_SEQ += 1
                        GUI_STATE = 1
                    else:
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 2:
                    gui_print('... Finding negative hard stop')
                    move('y', 1, zero = True)
                    ZERO_SEQ += 1
                elif ZERO_SEQ == 3:
                    if abs(y_stage.get_limit()):
                        gui_print('... Hard stop reached')
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 4:
                    gui_print('... Zeroing encoder and updating current position')
                    write_string_to_ser('z;y')
                    y_stage.cal_step_pos()
                    MOVE_NUM = 1
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                elif ZERO_SEQ == 5:
                    if MOVE_NUM == 1:
                        ACK = None
                        gui_print('... Moving to DATUM with coarse microsteps')
                        move('y', 1, to_datum = True)
                        GUI_STATE = 1
                    elif MOVE_NUM == 2:
                        if not y_stage.get_microstep():
                            gui_print('... Setting fine microsteps')
                            send_microstep('y', y_stage.get_move2_uS())
                            GUI_STATE = 1
                        else:
                            gui_print('... Finishing move to DATUM with fine microsteps')
                            move('y', 2, to_datum = True)
                            GUI_STATE = 1
                    elif MOVE_NUM == 3:
                        MOTOR_MASK = clearBit(MOTOR_MASK,1)
                        MOVE_NUM = 1
                        ZERO_SEQ = 1
                        gui_print('... Y Stage zeroing complete')
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,1)
                MOVE_NUM = 1
                ZERO_SEQ = 1
        elif testBit(MOTOR_MASK,0):
            if p_stage.get_status()[0]:
                if ZERO_SEQ == 1:
                    if p_stage.get_microstep():
                        gui_print('... Setting coarse microsteps')
                        send_microstep('p', p_stage.get_move1_uS())
                        ZERO_SEQ += 1
                        GUI_STATE = 1
                    else:
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 2:
                    gui_print('... Finding negative hard stop')
                    move('p', 1, zero = True)
                    ZERO_SEQ += 1
                elif ZERO_SEQ == 3:
                    if abs(p_stage.get_limit()):
                        gui_print('... Hard stop reached')
                        ZERO_SEQ += 1
                elif ZERO_SEQ == 4:
                    gui_print('... Zeroing encoder and updating current position')
                    write_string_to_ser('z;p')
                    p_stage.cal_step_pos()
                    MOVE_NUM = 1
                    ZERO_SEQ += 1
                    GUI_STATE = 1
                elif ZERO_SEQ == 5:
                    if MOVE_NUM == 1:
                        ACK = None
                        gui_print('... Moving to DATUM with coarse microsteps')
                        move('p', 1, to_datum = True)
                        GUI_STATE = 1
                    elif MOVE_NUM == 2:
                        if not p_stage.get_microstep():
                            gui_print('... Setting fine microsteps')
                            send_microstep('p', p_stage.get_move2_uS())
                            GUI_STATE = 1
                        else:
                            gui_print('... Finishing move to DATUM with fine microsteps')
                            move('p', 2, to_datum = True)
                            GUI_STATE = 1
                    elif MOVE_NUM == 3:
                        MOTOR_MASK = clearBit(MOTOR_MASK,0)
                        MOVE_NUM = 1
                        ZERO_SEQ = 1
                        gui_print('... P Stage zeroing complete')
            else:
                MOTOR_MASK = clearBit(MOTOR_MASK,0)
                MOVE_NUM = 1
                ZERO_SEQ = 1
        else:
            GUI_STATE = 0
            EXECUTING = False
        prev_GUI_STATE = 4

# Default Motion Parameters

# Default Instrument Parameters
x_datum_offset = 5 # mm
z_datum_offset = 50 # mm
y_datum_offset = 30 # deg
p_datum_offset = 30 # deg

lin_travel_range = 100 # mm
rot_travel_range = 60 # deg

def send_microstep(stage, microstep):
    if stage == 'x':
        uS_string = 't;x;' + str(microstep)
    elif stage == 'z':
        uS_string = 't;z;' + str(microstep)
    elif stage == 'y':
        uS_string = 't;y;' + str(microstep)
    elif stage == 'p':
        uS_string = 't;p;' + str(microstep)
    gui_print(uS_string)
    write_string_to_ser(uS_string)

def move(stage, move, zero = False, to_datum = False):
    global x_target, z_target, y_target, p_target
    global lin_travel_range, rot_travel_range
    global x_stage, z_stage, y_stage, p_stage
    if move == 1:
        if stage == 'x':
            if zero:
                move_string = x_stage.move_neg(lin_travel_range, 1, os_mult = 20)
            elif to_datum:
                move_string = x_stage.move_pos(abs(0-x_stage.get_true_position()), 1)
            else:
                if (x_target > x_stage.get_true_position()):
                    move_string = x_stage.move_pos(abs(x_target-x_stage.get_true_position()), 1)
                else:
                    move_string = x_stage.move_neg(abs(x_target-x_stage.get_true_position()), 1)
        if stage == 'z':
            if zero:
                move_string = z_stage.move_neg(lin_travel_range, 1, os_mult = 20)
            elif to_datum:
                move_string = z_stage.move_pos(abs(0-z_stage.get_true_position()), 1)
            else:
                if (z_target > z_stage.get_true_position()):
                    move_string = z_stage.move_pos(abs(z_target-z_stage.get_true_position()), 1)
                else:
                    move_string = z_stage.move_neg(abs(z_target-z_stage.get_true_position()), 1)
        if stage == 'y':
            if zero:
                move_string = y_stage.move_neg(rot_travel_range, 1, os_mult = 20)
            elif to_datum:
                move_string = y_stage.move_pos(abs(0-y_stage.get_true_position()), 1)
            else:
                if (y_target > y_stage.get_true_position()):
                    move_string = y_stage.move_pos(abs(y_target-y_stage.get_true_position()), 1)
                else:
                    move_string = y_stage.move_neg(abs(y_target-y_stage.get_true_position()), 1)
        if stage == 'p':
            if zero:
                move_string = p_stage.move_neg(rot_travel_range, 1, os_mult = 20)
            elif to_datum:
                move_string = p_stage.move_pos(abs(0-p_stage.get_true_position()), 1)
            else:
                if (p_target > p_stage.get_true_position()):
                    move_string = p_stage.move_pos(abs(p_target-p_stage.get_true_position()), 1)
                else:
                    move_string = p_stage.move_neg(abs(p_target-p_stage.get_true_position()), 1)
    elif move == 2:
        if stage == 'x':
            if to_datum:
                move_string = x_stage.move_neg(abs(x_target-x_stage.get_true_position()), 2)
            else:
                if (x_target > x_stage.get_true_position()):
                    move_string = x_stage.move_pos(abs(x_target-x_stage.get_true_position()), 2)
                else:
                    move_string = x_stage.move_neg(abs(x_target-x_stage.get_true_position()), 2)
        if stage == 'z':
            if to_datum:
                move_string = z_stage.move_neg(abs(z_target-z_stage.get_true_position()), 2)
            else:
                if (z_target > z_stage.get_true_position()):
                    move_string = z_stage.move_pos(abs(z_target-z_stage.get_true_position()), 2)
                else:
                    move_string = z_stage.move_neg(abs(z_target-z_stage.get_true_position()), 2)
        if stage == 'y':
            if to_datum:
                move_string = y_stage.move_neg(abs(y_target-y_stage.get_true_position()), 2)
            else:
                if (y_target > y_stage.get_true_position()):
                    move_string = y_stage.move_pos(abs(y_target-y_stage.get_true_position()), 2)
                else:
                    move_string = y_stage.move_neg(abs(y_target-y_stage.get_true_position()), 2)
        if stage == 'p':
            if to_datum:
                move_string = p_stage.move_neg(abs(p_target-p_stage.get_true_position()), 2)
            else:
                if (p_target > p_stage.get_true_position()):
                    move_string = p_stage.move_pos(abs(p_target-p_stage.get_true_position()), 2)
                else:
                    move_string = p_stage.move_neg(abs(p_target-p_stage.get_true_position()), 2)
    else:
        gui_print('Move command failed')
        return
    gui_print(move_string)
    write_string_to_ser(move_string)

def testBit(int_type, offset):
    # Credit to: https://wiki.python.org/moin/BitManipulation
    mask = 1 << offset
    return(int_type & mask)

def setBit(int_type, offset):
    # Credit to: https://wiki.python.org/moin/BitManipulation
    mask = 1 << offset
    return(int_type | mask)

def clearBit(int_type, offset):
    # Credit to: https://wiki.python.org/moin/BitManipulation
    mask = ~(1 << offset)
    return(int_type & mask)

def write_string_to_ser(string):
    global ACK_start
    ser.write(bytes(string.encode('utf-8')))
    ACK_start = time.time()

def update_status(status):
    global x_stage, z_stage, y_stage, p_stage
    x_stage.set_feedback(status[0],status[4])
    z_stage.set_feedback(status[1],status[5])
    y_stage.set_feedback(status[2],status[6])
    p_stage.set_feedback(status[3],status[7])
    x_status_frame.update_position("{0:.4f}".format(x_stage.get_position()[0]))
    z_status_frame.update_position("{0:.4f}".format(z_stage.get_position()[0]))
    y_status_frame.update_position("{0:.4f}".format(y_stage.get_position()[0]))
    p_status_frame.update_position("{0:.4f}".format(p_stage.get_position()[0]))
    x_status_frame.update_speed("{0:.2f}".format(x_stage.get_speed()))
    z_status_frame.update_speed("{0:.2f}".format(z_stage.get_speed()))
    y_status_frame.update_speed("{0:.2f}".format(y_stage.get_speed()))
    p_status_frame.update_speed("{0:.2f}".format(p_stage.get_speed()))
    if x_stage.get_limit() <0:
        x_status_frame.limit_on('m')
    elif x_stage.get_limit() >0:
        x_status_frame.limit_on('p')
    else:
        x_status_frame.limit_off('p')
        x_status_frame.limit_off('m')
    if z_stage.get_limit() <0:
        z_status_frame.limit_on('m')
    elif z_stage.get_limit() >0:
        z_status_frame.limit_on('p')
    else:
        z_status_frame.limit_off('p')
        z_status_frame.limit_off('m')
    if y_stage.get_limit() <0:
        y_status_frame.limit_on('m')
    elif y_stage.get_limit() >0:
        y_status_frame.limit_on('p')
    else:
        y_status_frame.limit_off('p')
        y_status_frame.limit_off('m')
    if p_stage.get_limit() <0:
        p_status_frame.limit_on('m')
    elif p_stage.get_limit() >0:
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

def save_motion_file():
    global x_stage, z_stage, y_stage, p_stage
    path = 'E:\\MUVI\\Manipulator\\Code_Repository\\thesis-manipulator\\MUVI_GUI\\motion_params.csv'
    mot_params = CSV_Read(path)
    write_params = []
    for row in range(2):
        row_data = []
        for col in range(45):
            row_data.append(mot_params.get_col_row(col+1,row+1))
        write_params.append(row_data)
    write_params[1][40] = str(x_stage.get_true_position())
    write_params[1][41] = str(z_stage.get_true_position())
    write_params[1][42] = str(y_stage.get_true_position())
    write_params[1][43] = str(p_stage.get_true_position())
    with open(path, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(write_params)
    writeFile.close()

def save_instrument_file():
    global x_stage, z_stage, y_stage, p_stage
    path = 'E:\\MUVI\\Manipulator\\Code_Repository\\thesis-manipulator\\MUVI_GUI\\instrument_params.csv'
    instr_params = CSV_Read(path)
    write_params = []
    for row in range(5):
        row_data = []
        for col in range(18):
            row_data.append(instr_params.get_col_row(col+1,row+1))
        write_params.append(row_data)
    write_params[1][0] = str(x_stage.get_datum())
    write_params[1][1] = str(z_stage.get_datum())
    write_params[1][2] = str(y_stage.get_datum())
    write_params[1][3] = str(p_stage.get_datum())
    with open(path, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(write_params)
    writeFile.close()

def shutdown_gui():
    log_filename = 'E:\\MUVI\\Manipulator\\Code_Repository\\thesis-manipulator\\MUVI_GUI\\Log_Files\\MUVI_Manipulator_log_'+ time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()) + '.csv'
    MUVI_log = log.get("1.0","end-1c").splitlines()
    with open(log_filename, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in MUVI_log:
            filewriter.writerow([line])
    save_motion_file()
    save_instrument_file()
    window.destroy()


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ------------------------------ Hardware  ------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

x_stage = NLS4.NewmarkLinearStage('x')
z_stage = NLS4.NewmarkLinearStage('z')
y_stage = RM5.NewmarkRotaryStage('y')
p_stage = RM5.NewmarkRotaryStage('p')

MUVI = manipulator.MUVI_manipulator(x_stage,z_stage,y_stage,p_stage)

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

# Control Row
control_frame = LabelFrame(window, text="Control Panel", bg='white')
control_frame.grid(row=8, column=0, rowspan=1, columnspan=50, sticky='WE', padx=5, pady=5)

Button(control_frame, text ="STOP", command = stop_manipulator, bg="red3", height=2, width=20, font=(None, 9, 'bold')).grid(row=1,column=0, sticky='W', padx=10, pady=5)

cmd_label = Label(control_frame, text="Send Command:", bg='white').grid(row=1,column=3, sticky=E)
cmd = Entry(control_frame, width = 25, bg="white", justify='right')
cmd.grid(row=1, column=4, columnspan = 4, sticky=W)
cmd.insert(0,'m;p;1000;1;50;1500;50')

Button(control_frame, text ="Send", command = send_cmd, height=2, width=20, bg='light blue').grid(row=1,column=9, sticky='W', padx=10, pady=5)

Button(control_frame, text ="Reset System", command = reset, height=2, width=20, bg='orange').grid(row=9,column=9, columnspan = 1, sticky='W', padx=10, pady=5)

Button(control_frame, text= "Move Stages", height=2, width=20, command=move_stages, bg='lime green').grid(row=9, column=0, sticky=W, padx=10, pady=5)

Button(control_frame, text= "Enable All", height=2, width=20, command=enable_all, bg='light blue').grid(row=9, column=3, sticky=W, padx=10, pady=5)

Button(control_frame, text= "Zero All", height=2, width=20, command=zero_all, bg='light blue').grid(row=9, column=6, sticky=W, padx=10, pady=5)

x_control_frame = control_box(control_frame, 10, 0, "mm", "X Translation", x_status_frame, x_stage)
z_control_frame = control_box(control_frame, 10, 3, "mm", "Z Translation", z_status_frame, z_stage)
y_control_frame = control_box(control_frame, 10, 6, "deg", "Yaw Rotation", y_status_frame, y_stage)
p_control_frame = control_box(control_frame, 10, 9, "deg", "Pitch Rotation", p_status_frame, p_stage)

x_control_frame.update_target('0.0000')
z_control_frame.update_target('0.0000')
y_control_frame.update_target('0.0000')
p_control_frame.update_target('0.0000')

x_control_frame.set_jogsize('0.0000')
z_control_frame.set_jogsize('0.0000')
y_control_frame.set_jogsize('0.0000')
p_control_frame.set_jogsize('0.0000')

# Test Panel Row
test_frame = LabelFrame(window, text="Test Panel", bg='white')
test_frame.grid(row=9, column=0, columnspan=50, sticky='WE', padx=5, pady=5)

Button(test_frame, text= "Load\nMotion Parameters", height=2, width=20, command=set_motion_params, bg='lightgoldenrod3').grid(row=26, column=1, columnspan = 3, sticky=W, padx=5, pady=3)

config_label = Label(test_frame, text="Config File:", bg='white').grid(row=26,column=7, sticky=E, padx=10, pady=5)
config = Entry(test_frame, width = 45, bg="white", justify='left')
config.grid(row=26, column=8, columnspan = 3, sticky=W)

Button(test_frame, text= "Load\nInstrument Parameters", height=2, width=20, command=set_instr_params, bg='lightgoldenrod3').grid(row=26, column=4, columnspan = 3, sticky=W, padx=5, pady=3)

Button(test_frame, text= "FOV Sweep", height=2, width=20, command=FOV_sweep, bg='light goldenrod').grid(row=27, column=1, columnspan = 3, sticky=W, padx=5, pady=3)

Button(test_frame, text= "Boresight", height=2, width=20, command=boresight, bg='light goldenrod').grid(row=27, column=4, columnspan = 3, sticky=W, padx=5, pady=3)

Button(test_frame, text= "Stray Light Sweep", height=2, width=20, command=SL_sweep, bg='light goldenrod').grid(row=27, column=7, columnspan = 3, sticky=W, padx=5, pady=3)

pitch_label = Label(test_frame, text="Pitch (\u03B8):", bg='white').grid(row=28,column=1, sticky=W, padx=5, pady=(10,3))
pitch = Entry(test_frame, width = 14, bg="white", justify='right')
pitch.grid(row=28, column=2, columnspan = 1, sticky=W, pady=(10,3))
pitch_units = Label(test_frame, text="deg", bg='white').grid(row=28,column=3, sticky=W, pady=(10,3))

pitch.insert(0,'0.0000')

yaw_label = Label(test_frame, text="Yaw (\u03C8):", bg='white').grid(row=28,column=4, sticky=W, padx=5, pady=(10,3))
yaw = Entry(test_frame, width = 14, bg="white", justify='right')
yaw.grid(row=28, column=5, columnspan = 1, sticky=W, pady=(10,3))
yaw_units = Label(test_frame, text="deg", bg='white').grid(row=28,column=6, sticky=W, pady=(10,3))

yaw.insert(0,'0.0000')

Button(test_frame, text= "Move Instrument", height=2, width=20, command=move_instrument, bg='lime green').grid(row=29, column=1, columnspan = 3, sticky=W, padx=5, pady=3)

Button(test_frame, text= "Capture Image", height=2, width=20, command=take_picture, bg='light goldenrod').grid(row=29, column=4, columnspan = 3, sticky=W, padx=5, pady=3)

Label(window, text="Created by: Jason Grillo \n Cal Poly Mechanical Engineering \n In Collaboration with UC Berkeley Space Sciences Laboratory \n \u00A9 2019, All Rights Reserved", bg='white',font=(None, 10)).grid(row=10,column=3)

log_label = Label(window, text="Manipulator Log", bg='white').grid(row=0,column=61, sticky=SE, padx=(0,80))
log = Text (window, width=55, height=31, takefocus=0, bg='white')
log.grid(row=1,rowspan=10, column = 60, columnspan = 3, sticky = NE, padx=5, pady=13)

gui_printer_label = Label(window, text="GUI Log", bg='white').grid(row=8,column=61, sticky=SE, padx=(0,100))
gui_printer = Text (window, width=55, height=10, takefocus=0, bg='white')
gui_printer.grid(row=9,rowspan=20, column = 60, columnspan = 3, sticky = NE, padx=5, pady=13)

timestamp = time.time() * 1000
log_print('|Timestamp (ms)|\tFeedback|\n', stamp = False)
gui_print('|Timestamp (ms)|\tFeedback|', stamp = False)

Button(window, text= "Save Data\nand Close", width=20, command=shutdown_gui, bg='orange').grid(row=0, column=62, columnspan = 3, sticky=SW, padx=5, pady=3)

# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# ----------------------------- Run the GUI -----------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

# Credit to: https://robotic-controls.com/learn/python-guis/tkinter-serial

# serialPort = "COM6"
serialPort = "COM7"
baudRate = 115200
try:
    ser = serial.Serial(serialPort , baudRate, timeout=0, writeTimeout=0, dsrdtr=True) #ensure non-blocking
    ser.flush()
    write_string_to_ser('r;r')  # reset the microcontroller
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
            log.see('end')  # show the last line printed
            gui_printer.see('end')
            serBuffer = "" # empty the buffer
        else:
            serBuffer += c # add to the buffer
    window.after(10, readSerial) # check serial again soon

# after initializing serial, a microcontroller may need a bit of time to reset
window.after(100, readSerial)

window.mainloop()
