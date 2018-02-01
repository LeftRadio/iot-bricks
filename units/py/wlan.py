#

from uplatform import WLAN, STA_IF, AP_IF
from uplatform import ( STAT_IDLE, STAT_CONNECTING, STAT_WRONG_PASSWORD,
                        STAT_NO_AP_FOUND, STAT_CONNECT_FAIL, STAT_GOT_IP )


class WLAN_STA_Manager(object):

    propertylist = b'alt_settings,alt_index,timeout'

    def __init__(self, **kwargs):
        self._name = kwargs['name']

        self._alt_settings = kwargs.get('alt_settings', ['SSID,PSWD'])
        assert len(self._alt_settings), 'no settings'
        self._alt_index = kwargs.get('alt_index', 0)

        self._timeout = kwargs.get('timeout', 30)
        self._time_cnt = -1

        self._auto_switch_config = True

        apwlan = WLAN(AP_IF)
        apwlan.active(False)

        self.itf = WLAN(STA_IF)
        self.itf.active(True)
        self.status = self.itf.status()
        self.status_cb = lambda x: x

        self._reset = False

    def set_property(self, attr, value):
        if attr == 'status':
            if self.status != value:
                setattr(self, attr, value)
                self.status_cb(value)
            return
        elif attr == '_alt_index':
            if value >= len(self._alt_settings):
                value = 0
        elif attr == '_reset':
            self.reset()
            value = False
        setattr(self, attr, value)

    def init(self):
        pass

    def reset(self):
        try:
            self.itf.disconnect()
        except Exception:
            pass
        self.itf.active(False)
        self.itf.active(True)

    def update(self, *args, **kwargs):
        seconds = kwargs.get('seconds', -1)
        st = self.itf.status()

        try:
            if st == STAT_GOT_IP or st == STAT_CONNECTING:
                pass
            elif st == STAT_IDLE:
                ssid, pswd = self._alt_settings[self._alt_index].split(',')
                self.itf.connect(ssid, pswd)
            else:
                assert st != STAT_WRONG_PASSWORD
                assert st != STAT_NO_AP_FOUND
                assert st != STAT_CONNECT_FAIL
        except Exception:
            if self._time_cnt == -1:
                self._time_cnt = seconds
            if seconds - self._time_cnt >= self._timeout:
                self._time_cnt = -1
                self.reset()
                if self._auto_switch_config:
                    self.set_property('_alt_index', self._alt_index + 1)

        self.set_property('status', st)
