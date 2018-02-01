
from base import BrickBase


class UserTimer(BrickBase):
    propertylist = b'enable,on,off,period'

    def __init__(self, **kwargs):
        super(UserTimer, self).__init__(**kwargs)
        self._start = kwargs.get('start', -1)
        self._on = kwargs.get('on', 0)
        self._off = kwargs.get('off', 0)
        self._period = kwargs.get('period', 0)

    def update(self, **kwargs):
        seconds = kwargs.get('seconds', -1)
        interval = kwargs.get('interval', 1)

        newstate = self._out_state

        if self._enable and seconds != -1:
            if self._start == -1:
                self._start = seconds
            tdelta = seconds - self._start
            if tdelta < 0:
                tdelta += self._period
            if tdelta >= self._period - interval:
                self._start = seconds + interval
            # on = 12:00, off = 13:00
            if self._off >= self._on:
                if self._off <= tdelta:
                    newstate = False
                elif self._on <= tdelta:
                    newstate = True
                else:
                    newstate = False
            # on = 13:00, off = 7:00
            else:
                if self._on <= tdelta:
                    newstate = True
                elif self._on >= tdelta and self._off <= tdelta:
                    newstate = False
                elif self._off >= tdelta:
                    newstate = True
                else:
                    newstate = False
        else:
            self._start = -1
            newstate = False

        if self._out_state == newstate:
            return

        self._out_state = newstate
        BrickBase.update_cb(self, 'update', out_state=self._out_state)

    def update_slot(self, sender, key, **kwargs):
        self._enable = kwargs.get('out_state', self._enable)


class Thermostat(BrickBase):
    propertylist = b'enable,intent,hys,mode,binded'

    def __init__(self, **kwargs):
        super(Thermostat, self).__init__(**kwargs)
        self._sourse_data = 0
        self._intent = kwargs.get('intent', -1)
        self._hys = kwargs.get('hys', 0)
        self._mode = kwargs.get('mode', 'heater')
        self._source_online = False

    def update(self, **kwargs):
        if self._enable and self._source_online:

            low_intent = self._intent - self._hys
            hight_intent = self._intent + self._hys

            if self._out_state:
                sth = ( self._mode in 'heater humidifier' and self._sourse_data >= hight_intent )
                stc = ( self._mode in 'cooler dryin' and self._sourse_data <= low_intent )
            else:
                sth = ( self._mode in 'heater humidifier' and self._sourse_data <= low_intent )
                stc = ( self._mode in 'cooler dryin' and self._sourse_data >= hight_intent )
            if sth or stc:
                self._out_state = False if self._out_state else True
            else:
                return
        else:
            if self._out_state:
                self._out_state = False
            else:
                return
        BrickBase.update_cb(self, 'update', out_state=self._out_state)

    def update_slot(self, sender, key, **kwargs):
        self._enable = kwargs.get('out_state', self._enable)
        #
        self._source_online = kwargs['online']
        if self._mode in 'heater cooler':
            self._sourse_data = kwargs['temp']
        elif self._mode in 'humidifier dryin':
            self._sourse_data = kwargs['humidity']
        else:
            return
