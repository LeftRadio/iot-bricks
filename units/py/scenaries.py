
from base import BrickBase


class UserTimer(BrickBase):
    propertylist = b'enable,on,off,period'

    def __init__(self, **kwargs):
        super(UserTimer, self).__init__(**kwargs)
        self.start = kwargs.get('start', -1)
        self.on = kwargs.get('on', 0)
        self.off = kwargs.get('off', 0)
        self.period = kwargs.get('period', 0)

    def update(self, seconds, interval):

        newstate = self.out_state

        if self.enable and seconds != -1:
            if self.start == -1:
                self.start = seconds
            tdelta = seconds - self.start
            if tdelta < 0:
                tdelta += self.period
            if tdelta >= self.period - interval:
                self.start = seconds + interval
            # on = 12:00, off = 13:00
            if self.off >= self.on:
                if self.off <= tdelta:
                    newstate = False
                elif self.on <= tdelta:
                    newstate = True
                else:
                    newstate = False
            # on = 13:00, off = 7:00
            else:
                if self.on <= tdelta:
                    newstate = True
                elif self.on >= tdelta and self.off <= tdelta:
                    newstate = False
                elif self.off >= tdelta:
                    newstate = True
                else:
                    newstate = False
        else:
            self.start = -1
            newstate = False

        if self.out_state == newstate:
            return

        self.out_state = newstate
        BrickBase.update_cb(self, self.out_state)

    def update_slot(self, sender, data):
        self.enable = True if data else False


class Thermostat(BrickBase):

    propertylist = b'enable,intent,hys,inverted,binded'

    def __init__(self, **kwargs):
        super(Thermostat, self).__init__(**kwargs)
        self.intent = kwargs.get('intent', -1)
        self.hys = kwargs.get('hys', 0)
        self.inverted = kwargs.get('inverted', False)
        self._sourse_data = -65535

    def update(self, seconds, interval):
        if self.enable:
            low_intent = self.intent - self.hys
            hight_intent = self.intent + self.hys
            if self.out_state:
                change_state = ( self._sourse_data >= hight_intent )
            else:
                change_state = ( self._sourse_data <= low_intent )
            if not change_state:
                return
            self.out_state ^= change_state
        else:
            if self.out_state:
                self.out_state = False
            else:
                return
        BrickBase.update_cb(self, bool(self.out_state ^ self.inverted))

    def update_slot(self, sender, data):
        self._sourse_data = data
