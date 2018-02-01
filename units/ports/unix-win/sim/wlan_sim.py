

STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_WRONG_PASSWORD = 2
STAT_NO_AP_FOUND = 3
STAT_CONNECT_FAIL = 4
STAT_GOT_IP = 5


class WLAN(object):
    """docstring for WLAN"""
    def __init__(self, *args, **kwargs):
        self.status = STAT_GOT_IP

    def status(self):
        return self.status

    def isconnected(self):
        return True
