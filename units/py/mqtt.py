
from uhashlib import sha256
from ubinascii import hexlify
from mqtt_base import MQTTClientBase

from defaults import MODULE_SERIAL_HASH
from uplatform import utime, json


class MQTTClient(MQTTClientBase):
    propertylist = b'alt_settings,alt_index'

    def __init__(self, **kwargs):
        super(MQTTClient, self).__init__(**kwargs)
        # load default settings
        if not len(self.alt_settings):
            self.alt_settings = MQTT_SETTINGS
        # server trust flag, set True only if module recived
        # self serial, then calc sha256 and compare with stored hash.
        self._server_trust = False
        # client state and state callback
        self.state = b'server_lost'
        self.state_callback = None

    def _except_setstate(self, ex):
        ex = str(ex)
        if '10035' in ex or 'TIMEDOUT' in ex:
            return
        if 'ABORT' in ex:
            self.set_property('state', b'server_lost')
        else:
            self.set_property('state', b'reset')
        self.disconnect()

    def _auth_server_request(self, try_cnt=3):
        while try_cnt:
            super().publish('services/client-auth', self.name, False, 0)
            utime.sleep(1)
            self.check_message(trustonly=False)
            if self._server_trust:
                return
            try_cnt -= 1
        raise OSError(-1)

    def _auth_server_respond(self, topic, msg):
        if b'client-auth' in topic:
            msg_hash = sha256(msg)
            if (hexlify(msg_hash.digest()) == MODULE_SERIAL_HASH):
                self._server_trust = True
                return
        raise OSError(-1)

    def _recive_msg(self, topic, msg):
        # check server auth state
        if not self._server_trust:
            self._auth_server_respond(topic, msg)
        # normal recive
        elif self.recived_cb:
            stopic = [ s for s in str(topic, 'utf-8').split('/') if s != '' ]
            data = json.loads(str(msg, 'utf-8')) if msg else None
            self.recived_cb( stopic[-2], stopic[-1], data )

    def group(self):
        return None

    def properties(self, **kwargs):
        if not len(kwargs):
            return {
                'classname': self.__class__.__name__,
                'name': self.name,
                'alt_index': self.alt_index,
                'alt_settings': self.alt_settings
            }
        for k, v in kwargs.values():
            self.set_property(k, v)

    def set_property(self, key, value):
        if key[0] == '_':
            return
        elif key == 'state':
            if self.state_callback:
                self.state_callback(value)
        elif key == 'alt_index':
            if value >= len(self.alt_settings):
                value = 0
            self.state = b'reset'
        setattr(self, key, value)

    def init(self):
        pass

    def update(self, seconds, interval):
        if self.state == b'reset':
            self.connect()
        elif self._server_trust:
            self.check_message()

    def connect(self, timeout=1):
        self._server_trust = False
        try:
            super().connect(timeout, True)
            self.subscribe(self.name+"/rx/#")
            self._auth_server_request(timeout)
            self.set_property('state', b'connected')
        except Exception as e:
            self._except_setstate(b'ABORT CONNECT')

    def disconnect(self):
        self._server_trust = False
        self.set_property('state', b'reset')
        try:
            super().disconnect()
        except Exception:
            pass

    def publish(self, topic, msg, retain=False, qos=0):
        if not self._server_trust:
            return
        try:
            topic = '%s/tx/%s/' % (self.name, topic)
            msg = bytes( json.dumps(msg), 'utf-8')
            super().publish(topic, msg, retain, qos)
        except Exception as e:
            self._except_setstate(e)

    def check_message(self, trustonly=True, timeout=0.05):
        if trustonly and not self._server_trust:
            return
        try:
            while 1:
                super().check_msg(timeout)
        except Exception as e:
            self._except_setstate(e)

