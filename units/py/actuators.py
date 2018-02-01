#

from base import BrickBase
from uplatform import Pin
from uplatform import utime


class Actuator(BrickBase):
    propertylist = b'enable,pin_index,active_low,out_state,binded'

    def __init__(self, **kwargs):
        super(Actuator, self).__init__(**kwargs)
        self.pin_index = kwargs.get('pin_index', 0)
        self.pin = None
        self.active_low = kwargs.get('active_low', True)
        self.set_property('pin_index', self.pin_index)

    def set_property(self, attr, value):
        super().set_property(attr, value)
        if attr == 'pin_index':
            self.pin = Pin(
                self.pin_index,
                Pin.OUT,
                self.out_state ^ self.active_low
            )

    def update(self, seconds, interval):
        pin_state = self.pin.value() ^ self.active_low
        if self.enable:
            if pin_state == self.out_state:
                return
        else:
            self.out_state = False
            if not pin_state:
                return
        self.pin.value(self.out_state ^ self.active_low)
        BrickBase.update_cb(self, self.out_state)

    def update_slot(self, sender, data):
        self.out_state = True if data else False
        self.update()


class Latch(Actuator):
    propertylist = b'enable,pin_index,active_low,binded'

    def update(self, seconds, interval):
        if not self.enable:
            self.pin.value(False ^ self.active_low)
            return
        self.pin.value(True ^ self.active_low)
        utime.sleep(0.05)
        self.pin.value(False ^ self.active_low)


class PWM(Actuator):
    pass
