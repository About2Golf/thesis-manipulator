"""
@author: Jason Grillo
"""

class NewmarkLinearStage:
    '''
    The class definition of a Linear Positioning Stage.
    '''
    def __init__(self, name):
        '''
        Initialize the stage. Default class member data is defined here, and
        may be updated if configuration files are used.
        @param name - The stage name, used when defining strings to send to the
                    microcontroller over serial.
        '''
        # Define the stage's name
        self.name = name
        # Define Default Motion/Instrument Parameters
        self.MC_Period = 25     # ms
        self.pos_dir = 1        # unitless
        self.init_speed = 50    # Hz
        self.max_speed = 500   # Hz
        self.accel = 50         # Hz
        self.mot_SPR = 200      # mot_deg/fullstep_deg
        self.pitch = 1.5875     # mm/rev
        self.enc_CPR = 4000     # counts/rev
        self.overshoot = 5      # steps
        self.move1_uS = 2       # microsteps/fullstep
        self.move2_uS = 64      # microsteps/fullstep
        self.datum = 25         # mm
        self.travel = 100       # mm
        # Define Position Variables
        self.encoder_restore = 0
        self.restored_encoder_offset = 0
        self.enc_pos = 0        # mm
        self.enc_prev_pos = 0   # mm
        self.enc_speed = 0      # mm/s
        self.step_pos = 0       # mm
        # self.true_position = 0  # mm
        self.lim = 0            # unitless
        self.direction = 1      # unitless
        self.enable_time = 0    # s
        # Define Flags
        self.ENABLED = False
        self.MOVING = False
        self.MICROSTEP_SET = False # True means move 2 microstep is set, False means move 1 microstep is set
        self.ZEROED = False
        self.RESTORED = False

    def move_neg(self, target, move, os_mult = 1):
        '''
        The method that calculates and defines the move string in the negative
        coordinate direction based on a target magnitude.
        @param target - The absolute target position to move the stage
        @param move - Indicates the first (coarse) or second (fine) move for microstep purposes
        @param os_mult - Multiplication factor for the number of steps to overshoot
        '''
        self.direction = -self.pos_dir
        if move == 1:
            steps = int(round(target*self.move1_uS*self.mot_SPR/self.pitch) - os_mult*self.overshoot)
        elif move == 2:
            steps = int(round(target*self.move2_uS*self.mot_SPR/self.pitch) - os_mult*self.overshoot)
        move_string = 'm;'+self.name+';'+ str(abs(steps))+';'+str(self.direction)+';'+str(self.init_speed)+';'+str(self.max_speed)+';'+str(self.accel)
        return move_string

    def move_pos(self, target, move, os_mult = 1):
        '''
        The method that calculates and defines the move string in the positive
        coordinate direction based on a target magnitude.
        @param target - The absolute target position to move the stage
        @param move - Indicates the first (coarse) or second (fine) move for microstep purposes
        @param os_mult - Multiplication factor for the number of steps to overshoot
        '''
        self.direction = self.pos_dir
        if move == 1:
            steps = round(target*self.move1_uS*self.mot_SPR/self.pitch) + os_mult*self.overshoot
        elif move == 2:
            steps = round(target*self.move2_uS*self.mot_SPR/self.pitch) + os_mult*self.overshoot
        move_string = 'm;'+self.name+';'+ str(abs(steps))+';'+str(self.direction)+';'+str(self.init_speed)+';'+str(self.max_speed)+';'+str(self.accel)
        return move_string

    def new_datum(self):
        '''
        Sets the current stage position as the new datum.
        '''
        self.datum += self.get_true_position()
        self.restored_encoder_offset = self.enc_pos

    def reset(self):
        '''
        Resets class member data to their default values.
        '''
        self.encoder_restore = 0
        self.restored_encoder_offset = 0
        self.enc_pos = 0
        self.enc_prev_pos = 0
        self.step_pos = 0
        self.enc_speed = 0
        self.lim = 0
        self.ENABLED = False
        self.MOVING = False
        self.MICROSTEP_SET = False # True means move 2 microstep is set, False means move 1 microstep is set
        self.ZEROED = False
        self.RESTORED = False

    def set_enable_time(self, value):
        '''
        Sets the enabled time parameter. Used to check how long the stage was
        enabled for timeout purposes.
        @param value - The time the stage was enabled.
        '''
        self.enable_time = value

    def set_microstep(self, value):
        '''
        Sets the microstep flag that indicates whether the stage is configured
        to coarse (FALSE) or fine (TRUE) microsteps.
        @param value - The microstep configuration of the stage.
        '''
        self.MICROSTEP_SET = value

    def set_enable(self, value):
        '''
        Sets the enabled flag that indicates whether or not the stage is enabled.
        @param value - The enable configuration of the stage
        '''
        self.ENABLED = value

    def set_moving(self, value):
        '''
        Sets the moving flag that indicates if the stage is currently moving to
        a target.
        @param value - Logical that indicates if the stage is moving or not
        '''
        self.MOVING = value

    def set_zeroed(self, value):
        '''
        Sets the zero flag that indicates whether or not the stage has been
        calibrated.
        @param value - The zero configuration of the stage
        '''
        self.ZEROED = True

    def set_encoder_restore(self,value):
        '''
        Sets the restored encoder value parameter.
        @param value - The restored encoder value
        '''
        self.encoder_restore = value

    def set_feedback(self, encoder, limit):
        '''
        This method calculates the encoder position based on the encoder count
        and updates the limit switch status.
        @param encoder - The position of the encoder in counts
        @param limit - The limit switch status
        '''
        self.lim = float(limit)
        if self.ZEROED:
            self.enc_pos = self.pos_dir*float(encoder)*self.pitch/self.enc_CPR - self.datum
        elif self.RESTORED:
            self.enc_pos = self.encoder_restore + self.pos_dir*float(encoder)*self.pitch/self.enc_CPR - self.restored_encoder_offset
        else:
            self.enc_pos = self.pos_dir*float(encoder)*self.pitch/self.enc_CPR
        self.enc_speed = 1000*(self.enc_pos - self.enc_prev_pos)/self.MC_Period
        self.enc_prev_pos = self.enc_pos

    def set_motion_params(self, param_list):
        '''
        This method updates the stage parameters that are defined in the
        motion parameters config file.
        @param param_list - A list of the motion parameters from the motion
                            parameters config file.
        '''
        self.pos_dir = int(param_list[0])
        self.init_speed = int(param_list[1])
        self.max_speed = int(param_list[2])
        self.accel = int(param_list[3])
        self.mot_SPR = float(param_list[4])
        self.pitch = float(param_list[5])
        self.enc_CPR = float(param_list[6])
        self.overshoot = int(param_list[7])
        self.move1_uS = int(param_list[8])
        self.move2_uS = int(param_list[9])
        self.encoder_restore = float(param_list[10])
        self.MC_Period = float(param_list[11])
        self.restored_encoder_offset = self.enc_pos # need this to offset the encoder reading when the set motion params method was called
        self.RESTORED = True

    def set_instrument_params(self, param_list):
        '''
        Updates the instrument specific parameters that are defined in the
        insturment parameters config file.
        @param param_list - A list of the motion parameters from the instrument
                            parameters config file.
        '''
        self.datum = float(param_list[0])
        self.travel = float(param_list[1])

    def set_step_pos(self, steps, move):
        '''
        Sets the current stage position based on the number of completed steps.
        The encoder position is separate from the step position - but the two
        should be fairly close to each other. The step position is recorded
        open loop.
        @param steps - The number of completed steps based on microcontroller feedback
        @param move - The move number that defines the microstep size (coarse or fine)
        '''
        if move == 1:
            self.step_pos += self.pos_dir*self.direction*float(steps)*self.pitch/(self.move1_uS*self.mot_SPR) + self.encoder_restore
        elif move == 2:
            self.step_pos += self.pos_dir*self.direction*float(steps)*self.pitch/(self.move2_uS*self.mot_SPR) + self.encoder_restore

    def cal_step_pos(self, type = 0):
        '''
        Calibrates the step position if steps were sent but the stage didn't move.
        @param type - Indicator used to distinguish if the step position needs to be
                    overidden by the encoder value.
        '''
        if type == 0:
            self.step_pos = -self.pos_dir*self.datum
            self.ZEROED = True
            self.RESTORED = False
        else:
            self.step_pos = self.enc_pos

    def get_true_position(self):
        '''
        Retrieves the current stage position based on the encoder feedback.
        @return enc_pos - The stage position defined by the encoder
        '''
        return self.enc_pos
        # if abs(self.enc_pos - self.step_pos) > 0.009:
        #     self.cal_step_pos(type=1)
        #     return self.enc_pos
        # else:
        #     return self.step_pos

    def get_status(self):
        '''
        Retrieves a list of the flag parameters that define the status
        of the stage.
        @return ENABLED - Flag indicating whether or not the stage is enabled
        @return MOVING - Flag indicating whether or not the stage is moving
        @return MICROSTEP_SET - Flag indicating whether or not the fine microstep is set
        @return ZEROED - Flag indicating whether or not the stage is zeroed
        '''
        return [self.ENABLED, self.MOVING, self.MICROSTEP_SET, self.ZEROED]

    def get_position(self):
        '''
        Retrieves the open loop and closed loop position of the stage.
        @return enc_pos - The closed loop position of the stage
        @return step_pos - The open loop position of the stage
        '''
        return [self.enc_pos, self.step_pos]

    def get_speed(self):
        '''
        Retrieves the calculated speed of the stage.
        @return enc_speed - The estimated speed based on the encoder position
        '''
        return self.enc_speed

    def get_limit(self):
        '''
        Retrieves the limit switch status of the stage based on the positive
        coordinate definition.
        @return lim - The limit switch status corrected by the positive direction
                    parameter
        '''
        return -self.lim*self.pos_dir

    def get_move1_uS(self):
        '''
        Retrieves the coarse microstep setting.
        @return move1_uS - The coarse microstep configuration
        '''
        return self.move1_uS

    def get_move2_uS(self):
        '''
        Retrieves the fine microstep setting.
        @return move2_uS - The fine microstep configuration
        '''
        return self.move2_uS

    def get_microstep(self):
        '''
        Retrieves the microstep status flag.
        @return MICROSTEP_SET - Flag indicating whether or not the fine microstep is set
        '''
        return self.MICROSTEP_SET

    def get_direction(self):
        '''
        Retrieves the direction parameter that defines the positive coordinate.
        @return direction - The positive coordinate direction
        '''
        return self.direction

    def get_datum(self):
        '''
        Retrieves the location of the stage's datum
        @return datum - The datum location defined from the hardstop
        '''
        return self.datum

    def get_enable_time(self):
        '''
        Retrieves the time the stage was last enabled.
        @param enable_time - The timestamp when the stage was enabled.
        '''
        return self.enable_time

    def get_name(self):
        '''
        Retrieves the stage's name for writing serial data to the microcontroller.
        @return name - The name of the stage
        '''
        return self.name
