
from uplatform import WLAN, STA_IF, AP_IF
from uplatform import ( STAT_IDLE, STAT_CONNECTING, STAT_WRONG_PASSWORD,
                        STAT_NO_AP_FOUND, STAT_CONNECT_FAIL, STAT_GOT_IP )
from defaults import WLAN_NAME_ID, WLAN_SETTINGS


class WLAN_STA_Manager(object):

    propertylist = b'alt_settings,alt_index,timeout'

    def __init__(self, **kwargs):

        self.name = kwargs.get('name', WLAN_NAME_ID)
        self.alt_settings = kwargs.get('alt_settings', WLAN_SETTINGS)
        self.alt_index = kwargs.get('alt_index', 0)

        self.timeout = kwargs.get('timeout', 10)
        self._time_cnt = -1

        self.auto_switch_config = True

        apwlan = WLAN(AP_IF)
        apwlan.active(False)

        self.itf = WLAN(STA_IF)
        self.itf.active(True)

        self.status = STAT_IDLE
        self.status_cb = None

    def group(self):
        return None

    def properties(self, **kwargs):
        if not len(kwargs):
            return {
                'classname': self.__class__.__name__,
                'name': self.name,
                'alt_index': self.alt_index,
                'alt_settings': self.alt_settings,
                'timeout': self.timeout
            }
        for k, v in kwargs.items():
            self.set_property(k, v)

    def set_property(self, key, value):
        if key == 'status' and self.status != value and self.status_cb:
            self.status_cb(value)
        elif key == 'alt_index' and value >= len(self.alt_settings):
            value = 0
        elif key == 'reset':
            self.reset()
            return
        setattr(self, key, value)

    def init(self):
        pass

    def reset(self):
        try:
            self.itf.disconnect()
        except Exception:
            pass
        self.itf.active(False)
        self.itf.active(True)
        self._time_cnt == -1

    def update(self, seconds, interval):
        st = self.itf.status()

        try:
            if st == STAT_GOT_IP or st == STAT_CONNECTING:
                pass
            elif st == STAT_IDLE:
                ssid, pswd = self.alt_settings[self.alt_index].split(',')
                self.itf.connect(ssid, pswd)
            else:
                assert st != STAT_WRONG_PASSWORD
                assert st != STAT_NO_AP_FOUND
                assert st != STAT_CONNECT_FAIL

        except Exception:
            if self._time_cnt == -1:
                self._time_cnt = seconds
            if seconds - self._time_cnt >= self.timeout:
                self.reset()

        self.set_property('status', st)
