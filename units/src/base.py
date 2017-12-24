#

objects_group = {
    'sensors': b'LM75,SHT21,DigitalInput,AnalogInput',
    'actuators': b'Actuator',
    'scenaries': b'UserTimer,Thermostat'
}


class BrickBase(object):

    update_cb = None

    def __init__(self, **kwargs):
        self._name = kwargs['name']
        self._enable = kwargs.get('enable', False)
        self._binded = kwargs.get('binded', False)
        if self._binded:
            self._out_state = False
        else:
            self._out_state = kwargs.get('out_state', False)

    def set_property(self, attr, value):
        setattr(self, attr, value)

    def init(self):
        pass

    def update_slot(self, sender, key, **kwargs):
        pass
