#
from mqtt_base import MQTTClientBase
from uplatform import json


class MQTTClient(MQTTClientBase):

    propertylist = b'alt_settings,alt_index,keepalive,ssl,ssl_params'

    def __init__(self, **kwargs):
        super(MQTTClient, self).__init__(**kwargs)
        self._name = kwargs['name']
        self.state = b'reset'
        self.state_cb = lambda x: x

    def _recive_msg(self, topic, msg):
        if self.recived_cb is not None:
            topic = [ s for s in str(topic, 'utf-8').split('/') if s != '' ]
            data = json.loads(str(msg, 'utf-8')) if msg else None
            self.recived_cb( topic[-2], topic[-1], data )

    def _ex_upd_state(self, ex):
        if 'ECONNABORTED' in str(ex):
            self.set_property('state', b'server_lost')
        elif '10035' in str(ex):
            return
        else:
            self.disconnect()
            self.set_property('state', b'reset')

    def set_property(self, attr, value):
        if attr == 'state':
            if self.state != value:
                setattr(self, attr, value)
                self.state_cb(value)
            return
        elif attr == '_alt_index':
            if value >= len(self._alt_settings):
                value = 0
        setattr(self, attr, value)

    def init(self):
        pass

    def update(self, **kwargv):
        if self.state == b'reset':
            self.connect()
        self.check_message()

    def connect(self):
        try:
            super().connect(0.5, True)
            self.subscribe(self._name+"/#")
            self.set_property('state', b'connected')
        except Exception:
            self._ex_upd_state(b'ECONNABORTED')

    def publish(self, topic, msg, retain=False, qos=0):
        if self.state != b'connected':
            return
        try:
            topic = '%s/%s/' % (self._name, topic)
            msg = bytes( json.dumps(msg), 'utf-8')
            super().publish(topic, msg, retain, qos)
        except Exception as e:
            self._ex_upd_state(e)

    def check_message(self):
        if self.state != b'connected':
            return
        try:
            while 1:
                super().check_msg()
        except Exception as e:
            self._ex_upd_state(e)
