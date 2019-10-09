"""
Created on Fri Feb  9 23:53:47 2018

@author: JasonGrillo
"""
import pyb
import micropython
import machine
import utime

import print_task

class Hub_Task:
    '''
    '''
    def __init__(self, x_params, z_params, y_params, p_params,
                    x_status, z_status, y_status, p_status,
                        x_enable, z_enable, y_enable, p_enable,
                            x_encoder, z_encoder, y_encoder, p_encoder,
                                x_zero, z_zero, y_zero, p_zero,
                                    x_limit, z_limit, y_limit, p_limit,
                                        x_csn_pin, z_csn_pin, y_csn_pin, p_csn_pin,
                                            dcen_pin):
        '''
        '''
        # self.print_q = printing_object
        # Motor Parameters Task Queue
        self.x_params = x_params
        self.z_params = z_params
        self.y_params = y_params
        self.p_params = p_params
        # Motor Status Task Share
        self.x_status = x_status
        self.z_status = z_status
        self.y_status = y_status
        self.p_status = p_status
        # Motor Enable Task Share
        self.x_enable = x_enable
        self.z_enable = z_enable
        self.y_enable = y_enable
        self.p_enable = p_enable
        # Encoder Zero Task Share
        self.x_zero = x_zero
        self.z_zero = z_zero
        self.y_zero = y_zero
        self.p_zero = p_zero
        # Encoder Value Task Share
        self.x_encoder = x_encoder
        self.z_encoder = z_encoder
        self.y_encoder = y_encoder
        self.p_encoder = p_encoder
        # Limit Switch Value Task Share
        self.x_limit = x_limit
        self.z_limit = z_limit
        self.y_limit = y_limit
        self.p_limit = p_limit
        # Chip Select Pins
        self.x_csn_pin =  machine.Pin(x_csn_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.z_csn_pin = machine.Pin(z_csn_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.y_csn_pin = machine.Pin(y_csn_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.p_csn_pin = machine.Pin(p_csn_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        # DC Step Enable Pin
        self.dcen_pin = machine.Pin(dcen_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        # Internal State Machine Motor Status
        self.X_POSITIONING = False
        self.Z_POSITIONING = False
        self.Y_POSITIONING = False
        self.P_POSITIONING = False
        # Serial Initialization
        self.uart = pyb.UART(2,115200)
        self.uart.init(115200, bits=8, parity=None, stop=1)
        self.spi2 = pyb.SPI(2,pyb.SPI.MASTER, prescaler=256, crc=0x7)

    def hub_fun(self):
        '''
        Defines the task function method that runs repeatedly.
        '''
        STATE_0 = micropython.const (0)
        STATE_1 = micropython.const (1)
        STATE_2 = micropython.const (2)
        STATE_3 = micropython.const (3)
        STATE_4 = micropython.const (4)
        STATE_5 = micropython.const (5)

        self.state = STATE_0

        while True:
            ## STATE 0: Initialize Stepper Drivers
            if self.state == STATE_0:
                self.TMC_init(self.y_csn_pin)
                yield()
                self.TMC_init(self.p_csn_pin)
                yield()
                self.TMC_init(self.z_csn_pin)
                yield()
                self.TMC_init(self.x_csn_pin)
                self.state = STATE_1

            ## STATE 1: IDLE
            if self.state == STATE_1:
                # self.update_feedback()
                self.read_GUI()
                yield()
                if self.Y_POSITIONING and self.y_enable.get():
                    self.Y_POSITIONING = False
                    self.state = STATE_2
                    # print("Moving Y")
                elif self.P_POSITIONING and self.p_enable.get():
                    self.P_POSITIONING = False
                    self.state = STATE_3
                    # print("Moving P")
                elif self.Z_POSITIONING and self.z_enable.get():
                    self.Z_POSITIONING = False
                    self.state = STATE_4
                    # print("Moving Z")
                elif self.X_POSITIONING and self.x_enable.get():
                    self.X_POSITIONING = False
                    self.state = STATE_5
                    # print("Moving X")

            ## STATE 2: MOVING YAW
            elif self.state == STATE_2:
                self.update_feedback()
                self.read_GUI()
                yield()
                # wait for motor to say done or limit reached or motor disabled
                if (self.y_status.get()) or abs(self.y_limit.get()) or not self.y_enable.get():
                    self.state = STATE_1

            ## STATE 3: MOVING PITCH
            elif self.state == STATE_3:
                self.update_feedback()
                self.read_GUI()
                yield()
                # wait for motor to say done or limit reached or motor disabled
                if (self.p_status.get()) or abs(self.p_limit.get()) or not self.p_enable.get():
                    self.state = STATE_1

            ## STATE 4: MOVING Z TRANSLATION
            elif self.state == STATE_3:
                self.update_feedback()
                self.read_GUI()
                yield()
                # wait for motor to say done or limit reached or motor disabled
                if (self.z_status.get()) or abs(self.z_limit.get()) or not self.z_enable.get():
                    self.state = STATE_1

            ## STATE 5: MOVING X TRANSLATION
            elif self.state == STATE_3:
                self.update_feedback()
                self.read_GUI()
                yield()
                # wait for motor to say done or limit reached or motor disabled
                if (self.x_status.get()) or (self.x_limit.get()) or not self.x_enable.get():
                    self.state = STATE_1
            print(self.state)
            yield(self.state)


# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def TMC_init(self, csn_pin):
        '''
        '''
        # spi_command1 = b'\xEC\x00\x01\x00\xC3'   # 256 microsteps
        spi_command1 = b'\xEC\x07\x01\x00\xC3'     # 2 microsteps
        spi_command2 = b'\x90\x00\x06\x1F\x0A'
        spi_command3 = b'\x91\x00\x00\x00\x0A'
        spi_command4 = b'\x80\x00\x00\x00\x04'
        spi_command5 = b'\x93\x00\x00\x01\xF4'
        csn_pin.value(0)
        self.spi2.send(spi_command1)
        # utime.sleep_us(10)
        self.spi2.send(spi_command2)
        # utime.sleep_us(10)
        self.spi2.send(spi_command3)
        # utime.sleep_us(10)
        self.spi2.send(spi_command4)
        # utime.sleep_us(10)
        self.spi2.send(spi_command5)
        # utime.sleep_us(10)
        csn_pin.value(1)
        self.dcen_pin.value(0)
        # !!!!! put dcen pin high here to setup DC STEP on the steppers

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def update_feedback(self):
        '''
        '''
        # print('updating feedback')
        # write the following to the GUI
        x_enc = str(self.x_encoder.get())
        z_enc = str(self.z_encoder.get())
        y_enc = str(self.y_encoder.get())
        p_enc = str(self.p_encoder.get())
        x_lim = str(self.x_limit.get())
        z_lim = str(self.z_limit.get())
        y_lim = str(self.y_limit.get())
        p_lim = str(self.p_limit.get())
        feedback_data = x_enc +";"+ z_enc +";"+ y_enc +";"+ p_enc +";"+ \
                            x_lim +";"+ z_lim +";"+ y_lim +";"+ p_lim
        # self.put_bytes(feedback_data.encode('UTF-8'))
        print(feedback_data.encode('UTF-8'))

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def read_GUI(self):
        ''' Reads the serial port for incoming commands and executes the command.
        '''
        # print('reading gui')
        # print(self.vcp.isconnected())
        # if self.vcp.any():
        #     print('command received')
        #     self.GUI_input = self.vcp.read().decode('UTF-8')
        #     self.GUI_Lookup_Table(self.GUI_input.split(";"))
        if self.uart.any():
            self.GUI_input = self.uart.read().decode('UTF-8')
            # self.GUI_Lookup_Table(self.GUI_input.split(";"))
            self.GUI_Lookup_Table(self.GUI_input)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def GUI_Lookup_Table(self, input):
        ''' Decodes GUI commands based on a defined list of commands.
        @param command The incoming GUI command to decode.
        Command Variations:
            "abort (a); axis (x,z,y,p)"
            "enable (e); axis (x,z,y,p)" or "disable (d); axis (x,z,y,p)"
            "move (m); axis (x,z,y,p); steps; direction; init speed; max speed; accel rate"
        '''
        command = input.split(";")
        action = command[0]
        axis = command[1]

        if action == "a":
            self.x_enable.put(0)
            self.z_enable.put(0)
            self.y_enable.put(0)
            self.p_enable.put(0)
            # shares.print_task.put_bytes(b'a')
            print(b'a')

        # ENABLE MOTOR
        elif action == "e":
            if axis == "x":
                self.x_enable.put(1)
            elif axis == "z":
                self.z_enable.put(1)
            elif axis == "y":
                self.y_enable.put(1)
            elif axis == "p":
                self.p_enable.put(1)
            # shares.print_task.put_bytes(b'e')
            print(b'e')

        # DISABLE MOTOR
        elif action == "d":
            if axis == "x":
                self.x_enable.put(0)
            elif axis == "z":
                self.z_enable.put(0)
            elif axis == "y":
                self.y_enable.put(0)
            elif axis == "p":
                self.p_enable.put(0)
            # shares.print_task.put_bytes(b'd')
            print(b'd')

        # MOVE MOTOR
        elif action == "m":
            steps = int(command[2])
            direction = int(command[3])
            init_speed = int(command[4])
            max_speed = int(command[5])
            accel_rate = int(command[6])
            if axis == "x":
                self.X_POSITIONING = True
                self.x_params.put(direction)
                self.x_params.put(init_speed)
                self.x_params.put(max_speed)
                self.x_params.put(accel_rate)
                self.x_params.put(steps)
            elif axis == "z":
                self.Z_POSITIONING = True
                self.z_params.put(direction)
                self.z_params.put(init_speed)
                self.z_params.put(max_speed)
                self.z_params.put(accel_rate)
                self.z_params.put(steps)
            elif axis == "y":
                self.Y_POSITIONING = True
                self.y_params.put(direction)
                self.y_params.put(init_speed)
                self.y_params.put(max_speed)
                self.y_params.put(accel_rate)
                self.y_params.put(steps)
            elif axis == "p":
                self.P_POSITIONING = True
                # print(type(input).encode('UTF-8'))
                # print(move[2].encode('UTF-8'))
                self.p_params.put(direction)
                self.p_params.put(init_speed)
                self.p_params.put(max_speed)
                self.p_params.put(accel_rate)
                self.p_params.put(steps)
            # shares.print_task.put_bytes(b'm')
            print(b'm')

        # ZERO
        elif action == "z":
            if axis == "x":
                self.x_zero.put(1)
            elif axis == "z":
                self.z_zero.put(1)
            elif axis == "y":
                self.y_zero.put(1)
            elif axis == "p":
                self.p_zero.put(1)
            # shares.print_task.put_bytes(b'z')
            print(b'z')
