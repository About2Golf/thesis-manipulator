"""
@author: Jason Grillo
"""

class MUVI_manipulator:
    def __init__(self, x_stage, z_stage, y_stage, p_stage):
        self.x_stage = x_stage
        self.z_stage = z_stage
        self.y_stage = y_stage
        self.p_stage = p_stage

        self.theta = 0
        self.psi = 0

        self.MOVING = False

    def set_enable_time(self, value):
        self.enable_time = value

    def set_instrument_params(self, param_list):
        self.datum = param_list[0]
        self.travel = param_list[1]

    def get_point_targets(theta_targ, psi_targ):

        y_deg = psi_targ
        p_deg = theta_targ
        return [x_mm, z_mm, y_deg, p_deg]

    def get_current_psi(self):
        return self.y_stage.get_true_position()

    def get_current_theta(self):
        return self.p_stage.get_true_position()
