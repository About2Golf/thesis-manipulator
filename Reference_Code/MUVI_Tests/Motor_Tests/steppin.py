import pyb
import micropython
import machine

micropython.alloc_emergency_exception_buf(100)

class StepPin(object):
    def __init__(self, timer, channel, pin, name):
        # self.pin=pyb.Pin(pin, pyb.Pin.AF_PP,af=3)
        # self.led = machine.Pin(led, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.pin = machine.Pin(pin, mode = machine.Pin.OUT, pull = machine.Pin.PULL_UP)
        self.timer = pyb.Timer(timer, freq=1)
        # self.channel = self.timer.channel(channel, pyb.Timer.PWM, pin=self.pin)
        self.channel = self.timer.channel(channel, pyb.Timer.OC_TIMING, callback=self.cb)
        self.stepping = 1
        self.name = name
        # self.channel.callback(self.cb)

    def start_stepping(self):
        self.stepping = 1
        # self.channel.callback(self.cb)

    def stop_stepping(self):
        self.stepping = 0
        # self.channel.callback(None)

    def set_freq(self,freq):
        self.timer.freq(freq)

    def cb(self, tim):
        if self.stepping:
            # print('stepping')
            # print(self.pin.value())
            if not self.pin.value():
                # print('pin high')
                self.pin.value(1)
                # self.channel.pulse_width_percent(50)
            else:
                # print('pin low')
                self.pin.value(0)
                # self.channel.pulse_width_percent(0)
        else:
            # print('not stepping')
            self.pin.value(0)
            # self.channel.pulse_width_percent(0)
