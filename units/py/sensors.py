
from base import BrickBase
from uplatform import I2C, Pin, ADC


class DigitalInput(BrickBase):
    propertylist = b'enable,pin_index'

    def __init__(self, **kwargs):
        super(BrickBase, self).__init__(**kwargs)
        self.out_state = bool(kwargs.get('value', 1) ^ 0x01)
        self.pin_index = kwargs.get('pin_index', 0)
        self.pin_mode = kwargs.get('pin_mode', Pin.IN)
        self.pin = None
        self.set_property('_pin_index', self.pin_index)

    def set_property(self, key, value):
        if key == 'pin_index':
            self.pin = Pin(value, self.pin_mode, self.out_state)
        super().set_property(key, value)

    def update(self, **kwargs):
        if self.enable:
            if self.out_state != self.pin.value():
                self.out_state = self.pin.value()
            else:
                return
        else:
            return
        BrickBase.update_cb(self, self.out_state)


class AnalogInput(BrickBase):
    propertylist = b'enable,pin_index,value'

    def __init__(self, **kwargs):
        super(BrickBase, self).__init__(**kwargs)
        self.out_state = None
        self.pin_index = kwargs.get('pin_index', 0)
        self.value = -1
        self.set_property('_pin_index', self.pin_index)

    def set_property(self, key, value):
        if key == 'pin_index':
            self._adc = ADC(value)
        super().set_property(key, value)

    def update(self, seconds, interval):
        if self.enable:
            newval = self._adc.read()
            if self.value == newval:
                return
            self.value = newval
        else:
            return
        BrickBase.update_cb(self, self.value)


class LM75(BrickBase):
    propertylist = b'enable,addr,thermo,temp'
    i2c = I2C(scl=Pin(12), sda=Pin(14), freq=100000)

    def __init__(self, **kwargs):
        super(LM75, self).__init__(**kwargs)
        self.addr = kwargs.get('addr', 0x48)
        self.thermo = kwargs.get('thermo', 0x48)
        self.temp = -65535
        try:
            rd = LM75.i2c.readfrom(self.addr, 2)
        except Exception:
            pass

    def update(self, seconds, interval):
        if not self.enable:
            return
        try:
            rd = LM75.i2c.readfrom(self.addr, 2)
            self.temp = rd[0]
        except Exception:
            self.temp = -65535
            self.thermo = -65535
        BrickBase.update_cb(self, self.temp)


class SHT21(BrickBase):
    propertylist = b'enable,addr,temp,humidity'
    i2c = I2C(scl=Pin(12), sda=Pin(14), freq=10000)

    def __init__(self, **kwargs):
        super(SHT21, self).__init__(**kwargs)
        self.addr = 0x40
        self.temp = -1
        self.humidity = -1

    def update(self, seconds, interval):
        if not self.enable:
            return
        from time import sleep
        try:
            SHT21.i2c.writeto(self.addr, bytearray([0xF3]))
            sleep(0.1)
            rd = SHT21.i2c.readfrom(self.addr, 3)
            rd = ((rd[0] << 8) + rd[1]) & 0xFFFC
            self.temp = (-46.85 + (175.72 * (rd / (2**16))))
            SHT21.i2c.writeto(self.addr, bytearray([0xF5]))
            sleep(0.1)
            rd = SHT21.i2c.readfrom(self.addr, 3)
            rd = ((rd[0] << 8) + rd[1]) & 0xFFFC
            self.humidity = (-6 + (125 * (rd / (2**16))))
        except Exception:
            try:
                SHT21.i2c.writeto(self.addr, bytearray([0xFE]))
            except Exception:
                pass
            self.temp = -1
            self.humidity = -1
        BrickBase.update_cb(self, (self.temp, self.humidity))
