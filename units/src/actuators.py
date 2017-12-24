#

from base import BrickBase
from uplatform import Pin


class Actuator(BrickBase):
    propertylist = b'enable,pin_index,active_low,out_state,binded'

    def __init__(self, **kwargs):
        super(Actuator, self).__init__(**kwargs)
        self._pin_index = kwargs.get('pin_index', 0)
        self._pin = None
        self.set_property('_pin_index', self._pin_index)
        self._active_low = kwargs.get('active_low', True)
        self._upd_out()

    def _upd_out(self):
        self._pin.value( self._out_state ^ self._active_low )

    def set_property(self, attr, value):
        super().set_property(attr, value)
        if attr == '_pin_index':
            self._pin = Pin( self._pin_index, Pin.OUT, self._out_state )

    def update(self, **kwargs):
        pin_state = True if self._pin.value() == 0 else False
        if self._enable:
            if pin_state == self._out_state:
                return
        else:
            self._out_state = False
            if not pin_state:
                return
        self._upd_out()
        BrickBase.update_cb(self, 'update', out_state=self._out_state)

    def update_slot(self, sender, key, **kwargs):
        self._out_state = kwargs['out_state']
        self.update()
