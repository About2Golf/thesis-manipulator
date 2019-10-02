# import tkinter as tk
from tkinter import *
from tkinter import messagebox
# from PIL import Image, ImageTk
import serial
import time


def enable_motor():
    selection = "You selected the option "

class status_box():
    def __init__(self,frame, row, column, units, name):
        self.row = row
        self.column = column
        self.units = units
        self.name = name
        self.status_frame = LabelFrame(frame, text=self.name, bg='white')
        self.status_frame.grid(row=self.row, column=self.column, rowspan=3, columnspan=3, sticky='WE', ipadx=5, ipady=5)

        self.pos_label = Label(self.status_frame, text="Position:", bg='white').grid(row=self.row,column=self.column, sticky=W)
        self.position = Entry(self.status_frame, width = 10, bg="gray80", justify='right')
        self.position.insert(0, "0123")
        self.position.grid(row=self.row, column=self.column+1, sticky=E)
        self.pos_units = Label(self.status_frame, text=self.units, bg='white').grid(row=self.row,column=self.column+2, sticky=W)

        self.speed_label = Label(self.status_frame, text="Speed:", bg='white').grid(row=(self.row+1),column=self.column, sticky=W)
        self.speed = Entry(self.status_frame, width = 10, bg="gray80", justify='right')
        self.speed.insert(0, "0123")
        self.speed.grid(row=(self.row+1), column=self.column+1, sticky=E)
        self.speed_units = Label(self.status_frame, text=(self.units+"/s"), bg='white').grid(row=(self.row+1),column=self.column+2, sticky=W)

        self.datum_label = Label(self.status_frame, text="Datum:", bg='white').grid(row=(self.row+2),column=self.column, sticky=W)
        self.datum = Entry(self.status_frame, width = 10, bg="gray80",  justify='right')
        self.datum.insert(0, "0123")
        self.datum.grid(row=(self.row+2), column=self.column+1, sticky=E)
        self.pos_units = Label(self.status_frame, text=self.units, bg='white').grid(row=(self.row+2),column=self.column+2, sticky=W)

class control_box():
    def __init__(self,frame, row, column, units, name):
        self.row = row
        self.column = column
        self.units = units
        self.name = name
        self.control_frame = LabelFrame(frame, text=self.name, bg='white')
        self.control_frame.grid(row=self.row, column=self.column, rowspan=3, columnspan=3, sticky='WE', ipadx=5, ipady=5)

        self.targ_label = Label(self.control_frame, text="Target:", bg='white').grid(row=self.row,column=self.column, sticky=W)
        self.target = Entry(self.control_frame, width = 10, bg="white", justify='right')
        # self.position.insert(0, "0123")
        self.target.grid(row=self.row, column=self.column+1, sticky=E)
        self.targ_units = Label(self.control_frame, text=self.units, bg='white').grid(row=self.row,column=self.column+2, sticky=W)

        self.jog_label = Label(self.control_frame, text="Jog Size:", bg='white').grid(row=(self.row+1),column=self.column, sticky=W)
        self.jog_size = Entry(self.control_frame, width = 10, bg="white", justify='right')
        # self.speed.insert(0, "0123")
        self.jog_size.grid(row=(self.row+1), column=self.column+1, sticky=E)
        self.jog_units = Label(self.control_frame, text=(self.units), bg='white').grid(row=(self.row+1),column=self.column+2, sticky=W)

        self.var = IntVar()
        self.enable_mot = Radiobutton(self.control_frame, text="Enable Motor", variable=self.var, value=1, command=enable_motor(), bg='white')
        self.enable_mot.grid(row=self.row, column=self.column+1, sticky=E)
        # self.enable_mot.set(None)



def stop_manipulator():
    # code to stop manipulator
    messagebox.showinfo("Manipulator Status","Manipulator stopped by user.")






window = Tk()
window.title("MUVI User Interface")
window.configure(background='white')
window.geometry("1000x1000")

# Top Row
cal_poly_logo = PhotoImage(file = "cal_poly_me_logo.gif")
Label (window, image=cal_poly_logo, bg="white") .grid(row=0, column = 0, stick = W)

Label(window, text="4 DOF Manipulator Interface", bg='white').grid(row=0,column=3)

ucb_logo = PhotoImage(file = "SSL-Berkeley-80blue.gif")
Label (window, image=ucb_logo, bg="white") .grid(row=0, column = 5, stick = W)

Button(window, text ="STOP", command = stop_manipulator, bg="red3", height=2, width=20).grid(row=1,column=0)

# Status Row
status_frame = LabelFrame(window, text="Status Panel", bg='white')
status_frame.grid(row=3, column=0, rowspan=5, columnspan=50, sticky='WE', ipadx=5, ipady=5)

x_status_frame = status_box(status_frame, 4, 0, "mm", "X Translation")
z_status_frame = status_box(status_frame, 4, 3, "mm", "Z Translation")
y_status_frame = status_box(status_frame, 4, 6, "deg", "Yaw Rotation")
p_status_frame = status_box(status_frame, 4, 9, "deg", "Pitch Rotation")

# Control Row
control_frame = LabelFrame(window, text="Control Panel", bg='white')
control_frame.grid(row=8, column=0, rowspan=5, columnspan=50, sticky='WE', ipadx=5, ipady=5)

x_control_frame = control_box(control_frame, 8, 0, "mm", "X Translation")
z_control_frame = control_box(control_frame, 8, 3, "mm", "Z Translation")
y_control_frame = control_box(control_frame, 8, 6, "deg", "Yaw Rotation")
p_control_frame = control_box(control_frame, 8, 9, "deg", "Pitch Rotation")





# ## X Status
# x_status_frame = LabelFrame(status_frame, text="X Translation")
# x_status_frame.grid(row=4, column=0, rowspan=3, columnspan=3, sticky='WE', ipadx=5, ipady=5)
#
# x_pos_label = Label(x_status_frame, text="Position:").grid(row=4,column=0, sticky=W)
# x_position = Entry(x_status_frame, width = 10, bg="gray80", justify='right')
# x_position.insert(0, "0123")
# x_position.grid(row=4, column=1, sticky=E)
# x_pos_units = Label(x_status_frame, text="mm").grid(row=4,column=2, sticky=W)
#
# x_speed_label = Label(x_status_frame, text="Speed:").grid(row=5,column=0, sticky=W)
# x_speed = Entry(x_status_frame, width = 10, bg="gray80", justify='right')
# x_speed.insert(0, "0123")
# x_speed.grid(row=5, column=1, sticky=E)
# x_speed_units = Label(x_status_frame, text="mm/s").grid(row=5,column=2, sticky=W)
#
# x_datum_label = Label(x_status_frame, text="Datum:").grid(row=6,column=0, sticky=W)
# x_datum = Entry(x_status_frame, width = 10, bg="gray80",  justify='right')
# x_datum.insert(0, "0123")
# x_datum.grid(row=6, column=1, sticky=E)
# x_pos_units = Label(x_status_frame, text="mm").grid(row=6,column=2, sticky=W)



# Open the GUI
window.mainloop()






# class App(Frame):
#     def __init__(self, master):
#         Frame.__init__(self, master)
#         self.columnconfigure(0,weight=1)
#         self.rowconfigure(0,weight=1)
#         self.original = Image.open('cal_poly_me_logo.gif')
#         self.image = ImageTk.PhotoImage(self.original)
#         self.display = Canvas(self, bd=0, highlightthickness=0)
#         self.display.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")
#         self.display.grid(row=0, sticky=W+E+N+S)
#         self.pack(fill=BOTH, expand=0)
#         self.bind("<Configure>", self.resize)
#
#     def resize(self, event):
#         size = (event.width, event.height)
#         resized = self.original.resize(size,Image.ANTIALIAS)
#         self.image = ImageTk.PhotoImage(resized)
#         self.display.delete("IMG")
#         self.display.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")
#
# root = Tk()
# root.geometry("1000x1000")
# app = App(root)
# app.mainloop()
# root.destroy()
