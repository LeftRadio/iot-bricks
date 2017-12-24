#
from mqtt_base import MQTTClientBase


class MQTTClient(MQTTClientBase):

    propertylist = b'server,port,user,pswd,keepalive,ssl,ssl_params'

    def __init__(self, **kwargs):
        super(MQTTClient, self).__init__(**kwargs)
        self._name = kwargs['name']
        self.state = b'reset'
        self.set_property = setattr

    def _recive_msg(self, topic, msg):
        if self.recived_cb is not None:
            topic = [ s for s in str(topic, 'utf-8').split('/') if s != '' ]
            from uplatform import json
            data = json.loads(str(msg, 'utf-8')) if msg else None
            self.recived_cb( topic[-2], topic[-1], data )

    def init(self):
        try:
            self.connect(0.5, True)
            self.subscribe(self._name+"/#")
            self.state = b'connected'
        except Exception:
            pass

    def update(self, **kwargv):
        if self.state == b'reset':
            self.init()
        self.check_message()

    def publish(self, topic, msg, retain=False, qos=0):
        if self.state != b'connected':
            return
        try:
            topic = '%s/%s/' % (self._name, topic)
            from uplatform import json
            msg = bytes( json.dumps(msg), 'utf-8')
            super().publish(topic, msg, retain, qos)
        except Exception as e:
            self.ex_upd_state(e)

    def check_message(self):
        if self.state != b'connected':
            return
        try:
            while 1:
                super().check_msg()
        except Exception as e:
            self.ex_upd_state(e)

    def ex_upd_state(self, ex):
        if 'ECONNABORTED' in str(ex):
            self.state = b'server_lost'
        elif '10035' in str(ex):
            return
        else:
            self.disconnect()
            self.state = b'reset'
