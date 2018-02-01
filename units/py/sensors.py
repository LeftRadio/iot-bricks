
from base import BrickBase
from uplatform import I2C, Pin, ADC


class DigitalInput(BrickBase):
    propertylist = b'enable,pin_index'

    def __init__(self, **kwargs):
        super(BrickBase, self).__init__(**kwargs)
        self._out_state = bool(kwargs.get('value', 1) ^ 0x01)
        self._pin_index = kwargs.get('pin_index', 0)
        self._pin_mode = kwargs.get('pin_mode', Pin.IN)
        self._pin = None
        self.set_property('_pin_index', self._pin_index)

    def set_property(self, attr, value):
        super().set_property(attr, value)
        if attr == '_pin_index':
            self._pin = Pin(self._pin_index, self._pin_mode, self._out_state)

    def update(self, **kwargs):
        if self._enable:
            if self._out_state != self._pin.value():
                self._out_state = self._pin.value()
            else:
                return
        else:
            return
        BrickBase.update_cb(self, 'update', out_state=self._out_state)


class AnalogInput(BrickBase):
    propertylist = b'enable,pin_index'

    def __init__(self, **kwargs):
        super(BrickBase, self).__init__(**kwargs)
        self._out_state = None
        self._pin_index = kwargs.get('pin_index', 0)
        self._value = -1
        self.set_property('_pin_index', self._pin_index)

    def set_property(self, attr, value):
        super().set_property(attr, value)
        if attr == '_pin_index':
            self._adc = ADC(self.value)

    def update(self, **kwargs):
        if self._enable:
            newval = self._adc.read()
            if self._value == newval:
                return
            self._value = newval
        else:
            return
        BrickBase.update_cb(self, 'update', analog=self._value)


class LM75(BrickBase):
    propertylist = b'enable,addr,thermo,temp'
    i2c = I2C(scl=Pin(12), sda=Pin(14), freq=100000)

    def __init__(self, **kwargs):
        super(LM75, self).__init__(**kwargs)
        self._addr = kwargs.get('addr', 0x48)
        self._thermo = kwargs.get('thermo', 0x48)
        self._temp = -1
        self._online = False
        try:
            rd = LM75.i2c.readfrom(self._addr, 2)
        except Exception:
            pass

    def update(self, **kwargs):
        if not self._enable:
            return
        try:
            rd = LM75.i2c.readfrom(self._addr, 2)
            self._temp = rd[0]
            self._online = True
        except Exception:
            self._temp = -1
            self._thermo = -10
            self._online = False
        BrickBase.update_cb(self, 'update', online=self._online, temp=self._temp)


class SHT21(BrickBase):
    propertylist = b'enable,addr,temp,humidity'
    i2c = I2C(scl=Pin(12), sda=Pin(14), freq=10000)

    def __init__(self, **kwargs):
        super(SHT21, self).__init__(**kwargs)
        self._addr = 0x40
        self._temp = -1
        self._humidity = -1
        self._online = False

    def update(self, **kwargs):
        if not self._enable:
            return
        from time import sleep
        try:
            SHT21.i2c.writeto(self._addr, bytearray([0xF3]))
            sleep(0.1)
            rd = SHT21.i2c.readfrom(self._addr, 3)
            rd = ((rd[0] << 8) + rd[1]) & 0xFFFC
            self._temp = (-46.85 + (175.72 * (rd / (2**16))))
            SHT21.i2c.writeto(self._addr, bytearray([0xF5]))
            sleep(0.1)
            rd = SHT21.i2c.readfrom(self._addr, 3)
            rd = ((rd[0] << 8) + rd[1]) & 0xFFFC
            self._humidity = (-6 + (125 * (rd / (2**16))))
            self._online = True
        except Exception:
            try:
                SHT21.i2c.writeto(self._addr, bytearray([0xFE]))
            except Exception:
                pass
            self._temp = -1
            self._humidity = -1
            self._online = False
        BrickBase.update_cb(self, 'update', online=self._online, temp=self._temp, humidity=self._humidity)
