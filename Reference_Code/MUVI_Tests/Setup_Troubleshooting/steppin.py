import pyb
import micropython
import machine

micropython.alloc_emergency_exception_buf(100)

class StepPin(object):
    def __init__(self, step_timer, step_channel, pin, init_speed, max_speed, accel_timer, accel_ch, accel_rate, name):
        # self.pin=pyb.Pin(pin, pyb.Pin.AF_PP,af=3)
        # self.led = machine.Pin(led, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.pin = machine.Pin(pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.init_speed = init_speed
        self.step_rate = self.init_speed
        self.max_step_rate = max_speed
        self.step_timer = pyb.Timer(step_timer, freq=self.step_rate)
        # self.channel = self.timer.channel(channel, pyb.Timer.PWM, pin=self.pin)
        self.step_channel = self.step_timer.channel(step_channel, pyb.Timer.OC_TIMING, callback=self.cb)
        self.accel_rate = accel_rate
        self.accel_timer = pyb.Timer(accel_timer, freq=self.accel_rate)
        # self.channel = self.timer.channel(channel, pyb.Timer.PWM, pin=self.pin)
        self.accel_channel = self.accel_timer.channel(accel_ch, pyb.Timer.OC_TIMING, callback=self.accel_cb)
        self.stepping = 0
        self.accelerating = 0
        self.step_count = 0
        self.total_steps = 0
        self.ramp_step_number = 0
        self.name = name

    def start_stepping(self, counts):
        self.stepping = 1
        self.accelerating = 1
        self.total_steps = 2*counts
        accel1 = round(self.total_steps*0.20)
        accel2 = round(self.max_step_rate*self.init_speed/self.accel_rate)
        self.accel_steps = min(accel1,accel2)
        self.steps_to_stop = self.total_steps - self.accel_steps
        # self.channel.callback(self.cb)

    def stop_stepping(self):
        self.stepping = 0
        self.accelerating = 0
        self.step_count = 0
        self.total_steps = 0
        self.step_rate = self.init_speed
        # self.channel.callback(None)

    def set_step_freq(self,step_rate):
        self.step_timer.freq(step_rate)

    def set_accel_rate(self,accel_rate):
        self.accel_timer.freq(accel_rate)

    def set_max_speed(self,max_step_rate):
        self.max_step_rate = max_step_rate

    def cb(self, tim):
        if self.stepping:
            self.step_count +=1
            if self.step_count <= self.total_steps:
                if not self.pin.value():
                    self.pin.value(1)
                else:
                    self.pin.value(0)
            else:
                self.stepping = 0
                self.accelerating = 0
                self.step_count = 0
                self.total_steps = 0
                self.step_rate = self.init_speed
                self.step_timer.freq(self.step_rate)
        else:
            self.pin.value(0)

    def accel_cb(self, tim):
        if self.accelerating:
            if self.step_count <= self.accel_steps:
                if self.step_rate < self.max_step_rate:
                    self.step_rate += 1
                    self.step_timer.freq(self.step_rate)
                # else:
                #     self.step_rate = self.max_step_rate
            elif self.step_count >= self.steps_to_stop:
                if self.step_rate > self.init_speed:
                    self.step_rate -= 1
                else:
                    self.step_rate = self.init_speed
                self.step_timer.freq(self.step_rate)
        else:
            return
