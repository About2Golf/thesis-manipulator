"""
Created on Fri Feb  9 23:53:47 2018

@author: JasonGrillo
"""
import micropython

class Hub_Task:
    '''
    '''

    def __init__(self, x_params, z_params, y_params, p_params, x_enable, z_enable, y_enable, p_enable, x_encoder, z_encoder, y_encoder, p_encoder, x_limit, z_limit, y_limit, p_limit):
        '''
        '''
        # self.HIGO = HIGO
        # self.HOGI = HOGI
        self.x_params = x_params
        self.z_params = z_params
        self.y_params = y_params
        self.p_params = p_params
        self.x_enable = x_enable
        self.z_enable = z_enable
        self.y_enable = y_enable
        self.p_enable = p_enable
        self.x_encoder = x_encoder
        self.z_encoder = z_encoder
        self.y_encoder = y_encoder
        self.p_encoder = p_encoder
        self.x_limit = x_limit
        self.z_limit = z_limit
        self.y_limit = y_limit
        self.p_limit = p_limit
        self.POSITIONING = False
        self.ZEROING = False
        self.vcp = pyb.USB_VCP ()

    def hub_fun(self):
        '''
        Defines the task function method.
        '''
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)
        STATE_3 = micropython.const (3)

        self.state = STATE_1

        while True:
            ## STATE 1: Listen for GUI Command
            if self.state == STATE_1:
                self.update_feedback()
                self.read_GUI()
                if self.POSITIONING:
                    self.POSITIONING = False
                    self.state = STATE_2
                elif: self.ZEROING:
                    self.ZEROING = False
                    self.state = STATE_3

            ## STATE 2: Positioning
            elif self.state == STATE_2:
                self.update_feedback()
                # wait for motor to say done
                if :
                    self.state = STATE_1

            ## STATE 3: Zeroing
            elif self.state == STATE_3:
                self.update_feedback()
                # wait for motor to say done
                if :
                    self.state = STATE_1

            yield(self.state)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def update_feedback(self):
        '''
        '''
        # write the following to the GUI
        self.x_encoder.get()
        self.z_encoder.get()
        self.y_encoder.get()
        self.p_encoder.get()
        self.x_limit.get()
        self.z_limit.get()
        self.y_limit.get()
        self.p_limit.get()
        self.vcp.send(self.feedback_data, timeout=5000)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def read_GUI(self):
        ''' Reads the serial port for incoming commands and executes the command.
        '''
        if self.vcp.any():
            self.INCOMING_DATA = True
            self.GUI_input = float(self.vcp.read(2).decode('UTF-8'))
            self.GUI_Lookup_Table(self.GUI_input)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def GUI_Lookup_Table(self, command):
        ''' Decodes GUI commands based on a defined list of commands
        @param command The incoming GUI command to decode
        '''
       # STOP
        if(command == 1):
            self.x_enable.put(0)
            self.z_enable.put(0)
            self.y_enable.put(0)
            self.p_enable.put(0)

        # MOVE TO POSITION
        elif(command == 2):

        # FIND HOME
        elif(command == 3):

        # FIND X ZERO
        elif(command == 4):

        # FIND Z ZERO
        elif(command == 5):

        # FIND YAW ZERO
        elif(command == 6):

        # FIND PITCH ZERO
        elif(command == 7):

        # ENABLE X MOTOR
        elif(command == 8):

        # ENABLE Z MOTOR
        elif(command == 9):

        # ENABLE YAW MOTOR
        elif(command == 10):

        # ENABLE PITCH MOTOR
        elif(command == 11):

        # # JOG X MINUS
        # elif(command == 12):
        #
        # # JOG X PLUS
        # elif(command == 13):
        #
        # # JOG Z MINUS
        # elif(command == 14):
        #
        # # JOG Z PLUS
        # elif(command == 15):
        #
        # # JOG YAW MINUS
        # elif(command == 16):
        #
        # # JOG YAW PLUS
        # elif(command == 17):
        #
        # # JOG PITCH MINUS
        # elif(command == 18):
        #
        # # JOG PITCH PLUS
        # elif(command == 19):

# command = 1; (STOP COMMAND)
# x_motor_enable = False
# z_motor_enable = False
# y_motor_enable = False
# p_motor_enable = False

# command = 2;
# x_motor: target=44.674,speed=10,accel=5.3
# z_motor: target=44.674,speed=10,accel=5.3
# y_motor: target=44.674,speed=10,accel=5.3
# p_motor: target=44.674,speed=10,accel=5.3

# command = 3;

# command = 4;

# command = 5;

# command = 6;

# command = 7;

# command = 8;
# x_enable = false

# command = 9;
# z_enable = true

# command = 10;
# y_enable = False

# command = 11;
# p_enable = false
