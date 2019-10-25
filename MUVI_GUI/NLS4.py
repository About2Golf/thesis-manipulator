"""
@author: Jason Grillo
"""

class NewmarkLinearStage:
    # def __init__(self, name, MC_Period, dir, init_speed, max_speed, accel, mot_SPR, pitch, enc_CPR, overshoot):
    def __init__(self, name):
        self.name = name

        self.MC_Period = 25     # ms
        self.pos_dir = 1        # unitless
        self.init_speed = 50    # Hz
        self.max_speed = 1500   # Hz
        self.accel = 50         # Hz
        self.mot_SPR = 200      # mot_deg/fullstep_deg
        self.pitch = 1.5875     # mm/rev
        self.enc_CPR = 4000     # counts/rev
        self.overshoot = 5      # steps
        self.move1_uS = 2       # microsteps/fullstep
        self.move2_uS = 256     # microsteps/fullstep
        self.datum = 50         # mm
        # self.range = 100        # mm

        self.enc_pos = 0        # mm
        self.enc_prev_pos = 0   # mm
        self.enc_speed = 0      # mm/s
        self.step_pos = 0       # mm
        # self.true_position = 0  # mm
        self.lim = 0            # unitless
        self.direction = 1      # unitless

        self.ENABLED = False
        self.MOVING = False
        self.MICROSTEP_SET = False # True means move 2 microstep is set, False means move 1 microstep is set
        self.ZEROED = False

    def move_neg(self, target, move, os_mult = 1):
        self.direction = -self.pos_dir
        if move == 1:
            steps = round(target*self.move1_uS*self.mot_SPR/self.pitch) - os_mult*self.overshoot
        elif move == 2:
            steps = round(target*self.move2_uS*self.mot_SPR/self.pitch) - os_mult*self.overshoot
        move_string = 'm;'+self.name+';'+ str(steps)+';'+str(self.direction)+';'+str(self.init_speed)+';'+str(self.max_speed)+';'+str(self.accel)
        return move_string

    def move_pos(self, target, move, os_mult = 1):
        self.direction = self.pos_dir
        if move == 1:
            steps = round(target*self.move1_uS*self.mot_SPR/self.pitch) + os_mult*self.overshoot
        elif move == 2:
            steps = round(target*self.move2_uS*self.mot_SPR/self.pitch) + os_mult*self.overshoot
        move_string = 'm;'+self.name+';'+ str(steps)+';'+str(self.direction)+';'+str(self.init_speed)+';'+str(self.max_speed)+';'+str(self.accel)
        return move_string

    def new_datum(self, datum):
        self.datum += self.get_true_position()

    def reset(self):
        self.enc_pos = 0
        self.enc_prev_pos = 0
        self.step_pos = 0
        self.enc_speed = 0
        self.lim = 0

    # def set_datum_to_position(self, value):

    def set_microstep(self, value):
        self.MICROSTEP_SET = value

    def set_enable(self, value):
        self.ENABLED = value

    def set_moving(self, value):
        self.MOVING = value

    def set_zeroed(self, value):
        self.ZEROED = True

    def set_feedback(self, encoder, limit):
        self.lim = float(limit)
        if self.ZEROED:
            self.enc_pos = self.pos_dir*float(encoder)*self.pitch/self.enc_CPR - self.datum
        else:
            self.enc_pos = self.pos_dir*float(encoder)*self.pitch/self.enc_CPR
        self.enc_speed = 1000*(self.enc_pos - self.enc_prev_pos)/self.MC_Period
        self.enc_prev_pos = self.enc_pos

    # def set_motion_params(self, MC_Period, dir, init_speed, max_speed, accel, mot_SPR, pitch, enc_CPR, overshoot, move1_uS, move2_uS):
    def set_motion_params(self, param_list):
        self.pos_dir = param_list[0]
        self.init_speed = param_list[1]
        self.max_speed = param_list[2]
        self.accel = param_list[3]
        self.mot_SPR = param_list[4]
        self.pitch = param_list[5]
        self.enc_CPR = param_list[6]
        self.overshoot = param_list[7]
        self.move1_uS = param_list[8]
        self.move2_uS = param_list[9]
        self.MC_Period = param_list[10]
        # self.range = range

    def set_instrument_params(self, param_list):
        self.datum = param_list[0]
        self.travel = param_list[1]

    def set_step_pos(self, steps, move):
        if move == 1:
            self.step_pos += self.pos_dir*self.direction*float(steps)*self.pitch/(self.move1_uS*self.mot_SPR)
        elif move == 2:
            self.step_pos += self.pos_dir*self.direction*float(steps)*self.pitch/(self.move2_uS*self.mot_SPR)

    def cal_step_pos(self, type = 0):
        if type == 0:
            self.step_pos = -self.pos_dir*self.datum
            self.ZEROED = True
        else:
            self.step_pos = self.enc_pos

    def get_true_position(self):
        if abs(self.enc_pos - self.step_pos) > 0.1:
            self.cal_step_pos(type=1)
            return self.enc_pos
        else:
            return self.step_pos

    def get_status(self):
        return [self.ENABLED, self.MOVING, self.MICROSTEP_SET, self.ZEROED]

    def get_position(self):
        return [self.enc_pos, self.step_pos]

    def get_speed(self):
        return self.enc_speed

    def get_limit(self):
        return self.lim*self.pos_dir

    def get_microstep(self):
        return self.MICROSTEP_SET

    def get_direction(self):
        return self.direction

    def get_name(self):
        return self.name
