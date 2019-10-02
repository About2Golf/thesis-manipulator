import pyb
import micropython
import machine

micropython.alloc_emergency_exception_buf(100)

class StepPin(object):
    def __init__(self, step_timer, step_channel, step_pin, dco_pin, init_speed, max_speed, accel_rate, accel_timer, accel_ch, name):
        self.step_pin = machine.Pin(step_pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.dco_pin = machine.Pin(dco_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.init_speed = init_speed
        self.step_rate = self.init_speed
        self.max_step_rate = max_speed
        self.step_timer = pyb.Timer(step_timer, freq=self.step_rate)
        self.step_channel = self.step_timer.channel(step_channel, pyb.Timer.OC_TIMING, callback=self.cb)
        self.accel_rate = accel_rate
        self.accel_timer = pyb.Timer(accel_timer, freq=self.accel_rate)
        self.accel_channel = self.accel_timer.channel(accel_ch, pyb.Timer.OC_TIMING, callback=self.accel_cb)
        self.stepping = 0
        self.accelerating = 0
        self.paused = 0
        self.step_count = 0
        self.total_steps = 0
        self.motor_steps = 200
        self.microsteps = 256
        self.name = name
        print('successfully created '+name)

    def move_to(self, steps):
        if steps == 0:
            return
        self.stepping = 1
        self.accelerating = 1
        self.total_steps = 2*steps
        accel1 = round(self.total_steps*0.20)
        accel2 = round(self.max_step_rate*self.init_speed/self.accel_rate)
        self.accel_steps = min(accel1,accel2)
        self.steps_to_stop = self.total_steps - self.accel_steps

    def rotate(self, degrees):
        steps = degrees * self.motor_steps * self.microsteps / 360
        self.move(steps)

    def stop(self):
        self.stepping = 0
        self.accelerating = 0
        self.step_count = 0
        self.total_steps = 0
        self.step_rate = self.init_speed

    def cb(self, tim):
        if self.stepping:
            if self.step_count <= self.total_steps:
                if self.dco_pin.value():
                    self.paused = 0
                    self.step_count +=1
                    if not self.step_pin.value():
                        self.step_pin.value(1)
                    else:
                        self.step_pin.value(0)
                else:
                    # self.paused = 1
                    # delete below for working version
                    self.paused = 0
                    self.step_count +=1
                    if not self.step_pin.value():
                        self.step_pin.value(1)
                    else:
                        self.step_pin.value(0)
            else:
                self.stepping = 0
                self.accelerating = 0
                self.step_count = 0
                self.total_steps = 0
                self.step_rate = self.init_speed
                self.step_timer.freq(self.step_rate)
        else:
            self.step_pin.value(0)

    def accel_cb(self, tim):
        if self.accelerating and not self.paused:
            if self.step_count <= self.accel_steps:
                if self.step_rate < self.max_step_rate:
                    self.step_rate += 1
                    self.step_timer.freq(self.step_rate)
            elif self.step_count >= self.steps_to_stop:
                if self.step_rate > self.init_speed:
                    self.step_rate -= 1
                else:
                    self.step_rate = self.init_speed
                self.step_timer.freq(self.step_rate)
        else:
            return

    def set_step_freq(self,step_rate):
        self.step_rate = step_rate
        self.step_timer.freq(self.step_rate)

    def set_accel_rate(self,accel_rate):
        self.accel_rate = accel_rate
        self.accel_timer.freq(self.accel_rate)

    def set_max_speed(self,max_step_rate):
        self.max_step_rate = max_step_rate

    def set_init_speed(self,init_speed):
        self.init_speed = init_speed
        self.set_step_freq(self.init_speed)
