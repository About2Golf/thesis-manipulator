"""
@author: Jason Grillo
"""

class NewmarkRotaryStage:
    # def __init__(self, name, MC_Period, dir, init_speed, max_speed, accel, mot_SPR, gear_ratio, enc_CPR, overshoot):
    def __init__(self, name):
        self.name = name
        self.MC_Period = 50
        self.direction = 1
        self.init_speed = 50
        self.max_speed = 1500
        self.accel = 50
        self.mot_SPR = 200
        self.gear_ratio = 72
        self.enc_CPR = 4000
        self.overshoot = 5

        self.enc_pos = 0
        self.enc_prev_pos = 0
        self.step_pos = 0
        self.enc_speed = 0
        self.lim = 0

        self.ENABLED = False
        self.MOVING = False
        self.MICROSTEP_SET = False # True means move 2 microstep is set, False means move 1 microstep is set
        self.ZEROED = False

    def move_neg(self, target):
        return

    def move_pos(self, target):
        return

    def zero(self):
        return

    def reset(self):
        return

    def set_microstep(self, uS):
        return

    def set_enable(self):
        return

    def set_disable(self):
        return

    def set_acknowledge(self, ACK):
        return

    def set_feedback(self, encoder, limit):
        self.lim = float(limit)
        self.enc_pos = self.direction*float(encoder)*360/(self.enc_CPR*self.gear_ratio)
        self.enc_speed = 1000*(self.enc_pos - self.enc_prev_pos)/self.MC_Period
        self.enc_prev_pos = self.enc_pos
        # y_direction_param*float(status[2])*360/(rot_enc_CPR*rot_gear_ratio)

    def set_motion_params(self, MC_Period, dir, init_speed, max_speed, accel, mot_SPR, gear_ratio, enc_CPR, overshoot):
        self.MC_Period = MC_Period
        self.direction = dir
        self.init_speed = init_speed
        self.max_speed = max_speed
        self.accel = accel
        self.mot_SPR = mot_SPR
        self.gear_ratio = gear_ratio
        self.enc_CPR = enc_CPR
        self.overshoot = overshoot

    def convert_enc_to_steps(self):
        return self.enc_pos*self.enc_CPR/(self.direction*self.pitch)

    def get_status(self):
        return [self.ENABLED, self.MOVING, self.MICROSTEP_SET, self.ZEROED]

    def get_position(self):
        return [self.enc_pos, self.step_pos]

    def get_speed(self):
        return self.enc_speed

    def get_limit(self):
        return self.lim

    def get_microstep(self):
        return self.MICROSTEP_SET
