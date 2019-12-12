"""
@author: JasonGrillo
"""
import pyb
import micropython
import machine
import utime

class Hub_Task:
    '''
    This defines the task object for the hub. The hub is purposed to be the
    information processing center for the manipulator, and handles the GUI
    input and output. The hub also handles the TMC2160 stepper driver
    configuration via SPI.
    '''
    def __init__(self, x_params, z_params, y_params, p_params,
                x_steps, z_steps, y_steps, p_steps,
                    x_status, z_status, y_status, p_status,
                        x_enable, z_enable, y_enable, p_enable,
                            x_encoder, z_encoder, y_encoder, p_encoder,
                                x_zero, z_zero, y_zero, p_zero,
                                    x_limit, z_limit, y_limit, p_limit,
                                        x_csn_pin, z_csn_pin, y_csn_pin, p_csn_pin,
                                            dcen_pin):
        '''
        The initialization method for the hub class object. The shared data is
        defined and hardware pins are defined. Class data is also declared upon
        startup.
        @param x_params - X stage motor parameters Queue
        @param z_params - Z stage motor parameters Queue
        @param y_params - Y stage motor parameters Queue
        @param p_params - P stage motor parameters Queue
        @param x_steps - X stage completed steps Queue
        @param z_steps - Z stage completed steps Queue
        @param y_steps - Y stage completed steps Queue
        @param p_steps - P stage completed steps Queue
        @param x_status - X stage motion status Share (done moving or not)
        @param z_status - Z stage motion status Share (done moving or not)
        @param y_status - Y stage motion status Share (done moving or not)
        @param p_status - P stage motion status Share (done moving or not)
        @param x_enable - X motor enable Share
        @param z_enable - Z motor enable Share
        @param y_enable - Y motor enable Share
        @param p_enable - P motor enable Share
        @param x_encoder - X encoder feedback data Share
        @param z_encoder - Z encoder feedback data Share
        @param y_encoder - Y encoder feedback data Share
        @param p_encoder - P encoder feedback data Share
        @param x_zero - X zero encoder command Share
        @param z_zero - Z zero encoder command Share
        @param y_zero - Y zero encoder command Share
        @param p_zero - P zero encoder command Share
        @param x_limit - X limit switch feedback data Share
        @param z_limit - Z limit switch feedback data Share
        @param y_limit - Y limit switch feedback data Share
        @param p_limit - P limit switch feedback data Share
        @param x_csn_pin - X hardware pin for SPI chip select
        @param z_csn_pin - Z hardware pin for SPI chip select
        @param y_csn_pin - Y hardware pin for SPI chip select
        @param p_csn_pin - P hardware pin for SPI chip select
        @param dcen_pin - DC step pin for TMC2160 Cool Step operation
        '''
        # Motor Parameters Task Queue
        self.x_params = x_params
        self.z_params = z_params
        self.y_params = y_params
        self.p_params = p_params
        # Motor Steps Task Queue
        self.x_steps = x_steps
        self.z_steps = z_steps
        self.y_steps = y_steps
        self.p_steps = p_steps
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
        self.x_csn_pin.value(1)
        self.z_csn_pin.value(1)
        self.y_csn_pin.value(1)
        self.p_csn_pin.value(1)
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
        # TMC Init Commands
        self.spi_command1_256 = b'\xEC\x00\x01\x00\xC3'  # 256 microsteps
        self.spi_command1_128 = b'\xEC\x01\x01\x00\xC3'  # 128 microsteps
        self.spi_command1_64 = b'\xEC\x02\x01\x00\xC3'   # 64 microsteps
        self.spi_command1_32 = b'\xEC\x03\x01\x00\xC3'   # 32 microsteps
        self.spi_command1_16 = b'\xEC\x04\x01\x00\xC3'   # 16 microsteps
        self.spi_command1_8 = b'\xEC\x05\x01\x00\xC3'    # 8 microsteps
        self.spi_command1_4 = b'\xEC\x06\x01\x00\xC3'    # 4 microsteps
        self.spi_command1_2 = b'\xEC\x07\x01\x00\xC3'    # 2 microsteps
        self.spi_command1_0 = b'\xEC\x08\x01\x00\xC3'    # 0 microsteps
        self.spi_command2 = b'\x90\x00\x06\x1F\x0A'
        self.spi_command3 = b'\x91\x00\x00\x00\x0A'
        self.spi_command4 = b'\x80\x00\x00\x00\x04'
        self.spi_command5 = b'\x93\x00\x00\x01\xF4'

    def hub_fun(self):
        '''
        Defines the hub task state machine that is repeatedly called.
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
                self.update_feedback()
                yield()
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
                if self.y_status.get():
                    self.steps_moved = 's;y;' + str(self.y_steps.get())
                    print(self.steps_moved)
                    self.state = STATE_1

            ## STATE 3: MOVING PITCH
            elif self.state == STATE_3:
                self.update_feedback()
                self.read_GUI()
                yield()
                if self.p_status.get():
                    self.steps_moved = 's;p;' + str(self.p_steps.get())
                    print(self.steps_moved)
                    self.state = STATE_1

            ## STATE 4: MOVING Z TRANSLATION
            elif self.state == STATE_4:
                self.update_feedback()
                self.read_GUI()
                if self.z_status.get():
                    self.steps_moved = 's;z;' + str(self.z_steps.get())
                    print(self.steps_moved)
                    self.state = STATE_1

            ## STATE 5: MOVING X TRANSLATION
            elif self.state == STATE_5:
                self.update_feedback()
                self.read_GUI()
                yield()
                if self.x_status.get():
                    self.steps_moved = 's;x;' + str(self.x_steps.get())
                    print(self.steps_moved)
                    self.state = STATE_1

            yield(self.state)


# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def TMC_init(self, csn_pin):
        '''
        This method intitializes a TMC2160 stepper driver upon startup.
        @param csn_pin The stepper driver SPI chip select pin
        '''
        csn_pin.value(0)
        self.spi2.send(self.spi_command1_2)
        utime.sleep_us(5)
        csn_pin.value(1)
        utime.sleep_us(5)
        csn_pin.value(0)
        self.spi2.send(self.spi_command2)
        utime.sleep_us(5)
        csn_pin.value(1)
        utime.sleep_us(5)
        csn_pin.value(0)
        self.spi2.send(self.spi_command3)
        utime.sleep_us(5)
        csn_pin.value(1)
        utime.sleep_us(5)
        csn_pin.value(0)
        self.spi2.send(self.spi_command4)
        utime.sleep_us(5)
        csn_pin.value(1)
        utime.sleep_us(5)
        csn_pin.value(0)
        self.spi2.send(self.spi_command5)
        utime.sleep_us(5)
        csn_pin.value(1)
        # put dcen pin high here to setup DC STEP on the steppers
        self.dcen_pin.value(0)

    def set_TMC_microstep(self, command, csn_pin):
        '''
        This method sets the microstep setting for the TMC2160 stepper driver.
        @param command - The microstep SPI command to send
        @param csn_pin - The stepper driver SPI chip select pin
        '''
        if command == 1:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_0)
            csn_pin.value(1)
        elif command == 2:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_2)
            csn_pin.value(1)
        elif command == 4:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_4)
            csn_pin.value(1)
        elif command == 8:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_8)
            csn_pin.value(1)
        elif command == 16:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_16)
            csn_pin.value(1)
        elif command == 32:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_32)
            csn_pin.value(1)
        elif command == 64:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_64)
            csn_pin.value(1)
        elif command == 128:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_128)
            csn_pin.value(1)
        elif command == 256:
            csn_pin.value(0)
            self.spi2.send(self.spi_command1_256)
            csn_pin.value(1)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def update_feedback(self):
        '''
        This method reads the feedback shared variables and prints the data
        for the GUI to receive in the serial port.
        '''
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
        print(feedback_data)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def read_GUI(self):
        ''' Reads the serial port for incoming commands and executes the command.
        '''
        if self.uart.any():
            self.GUI_input = self.uart.read().decode('UTF-8')
            self.GUI_Lookup_Table(self.GUI_input)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
    def GUI_Lookup_Table(self, input):
        ''' Decodes GUI commands based on a defined list of commands. Once
        received, an acknowledgement is printed so the GUI knows the
        command was processed.
        @param input - The incoming GUI command to decode and act upon.
        Command Variations:
            "abort (a); axis (x,z,y,p)"
            "enable (e); axis (x,z,y,p)" or "disable (d); axis (x,z,y,p)"
            "move (m); axis (x,z,y,p); steps; direction; init speed; max speed; accel rate"
            "zero (z); axis (x,z,y,p)"
            "microstep (t); axis (x,z,y,p); microsteps per fullstep"
            "reset (r)"
        '''
        command = input.split(";")
        action = command[0]
        axis = command[1]

        if action == "a":
            self.x_enable.put(0)
            self.z_enable.put(0)
            self.y_enable.put(0)
            self.p_enable.put(0)
            print('a')

        # ENABLE MOTOR
        elif action == "e":
            if axis == "x":
                self.x_enable.put(1)
                print('e;x')
            elif axis == "z":
                self.z_enable.put(1)
                print('e;z')
            elif axis == "y":
                self.y_enable.put(1)
                print('e;y')
            elif axis == "p":
                self.p_enable.put(1)
                print('e;p')

        # DISABLE MOTOR
        elif action == "d":
            if axis == "x":
                self.x_enable.put(0)
                print('d;x')
            elif axis == "z":
                self.z_enable.put(0)
                print('d;z')
            elif axis == "y":
                self.y_enable.put(0)
                print('d;y')
            elif axis == "p":
                self.p_enable.put(0)
                print('d;p')

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
                print('m;x')
            elif axis == "z":
                self.Z_POSITIONING = True
                self.z_params.put(direction)
                self.z_params.put(init_speed)
                self.z_params.put(max_speed)
                self.z_params.put(accel_rate)
                self.z_params.put(steps)
                print('m;z')
            elif axis == "y":
                self.Y_POSITIONING = True
                self.y_params.put(direction)
                self.y_params.put(init_speed)
                self.y_params.put(max_speed)
                self.y_params.put(accel_rate)
                self.y_params.put(steps)
                print('m;y')
            elif axis == "p":
                self.P_POSITIONING = True
                self.p_params.put(direction)
                self.p_params.put(init_speed)
                self.p_params.put(max_speed)
                self.p_params.put(accel_rate)
                self.p_params.put(steps)
                print('m;p')

        # ZERO
        elif action == "z":
            if axis == "x":
                self.x_zero.put(1)
                print('z;x')
            elif axis == "z":
                self.z_zero.put(1)
                print('z;z')
            elif axis == "y":
                self.y_zero.put(1)
                print('z;y')
            elif axis == "p":
                self.p_zero.put(1)
                print('z;p')

        # SEND TMC COMMAND
        elif action == "t":
            if axis == "x":
                self.set_TMC_microstep(int(command[2]), self.x_csn_pin)
                print('t;x'+';'+command[2])
            elif axis == "z":
                self.set_TMC_microstep(int(command[2]), self.z_csn_pin)
                print('t;z'+';'+command[2])
            elif axis == "y":
                self.set_TMC_microstep(int(command[2]), self.y_csn_pin)
                print('t;y'+';'+command[2])
            elif axis == "p":
                self.set_TMC_microstep(int(command[2]), self.p_csn_pin)
                print('t;p'+';'+command[2])

        # RESET
        elif action == "r":
            print('Resetting the RTOS')
            pyb.hard_reset()
