
import re
import hashlib
import paho.mqtt.client as mqtt
from time import sleep


class BricksClientAuth(object):
    """docstring for BricksClientAuth"""

    SYS_TOPIC = '$SYS/broker/log/N'
    SERV_TOPIC = 'services/client-auth'

    def __init__(self, name='IOT-BRICKS-CLIENTS-AUTH'):
        self.clients_base = {'iot_brick_esp_32_123_2_0': b'MDL0001S'}
        self.connected_clients = []
        #
        self.mqtt = mqtt.Client(name)
        self.mqtt.username_pw_set('admin', password='admin')
        self.mqtt.tls_set('/home/leftradio/ssl_test/ca.crt', tls_version=2)
        self.mqtt.reconnect_delay_set(min_delay=1, max_delay=1)
        #
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_disconnect = self.on_disconnect
        self.mqtt.on_message = self.on_message
        #
        self.mqtt.message_callback_add(self.SYS_TOPIC, self._peer_connect)
        #
        self.mqtt.message_callback_add(self.SERV_TOPIC, self._peer_request)
        #
        self.connected = False
        self.start = True

    def _peer_connect(self, client, data, msg):
        topic = msg.topic
        data = msg.payload.decode('utf-8')
        try:
            client_name = re.findall(r'iot_brick_\w+\d+\b', data)[0]
            if client_name not in self.clients_base:
                raise Exception
        except Exception as e:
            return

        if 'disconnect' in data:
            if client_name in self.connected_clients:
                self.connected_clients.remove(client_name)
        elif 'connect' in data:
            if client_name in self.connected_clients:
                self.connected_clients.remove(client_name)
                self.connected_clients.append(client_name)

    def _peer_request(self, client, data, msg):
        topic = msg.topic
        client_name = msg.payload.decode('utf-8')
        self.mqtt.publish( client_name+'/rx/client-auth', self.clients_base[client_name] )

    def run(self):
        while self.start:
            try:
                if not self.connected:
                    self.mqtt.connect("iot-bricks-server.local", 8883, 60)
                    self.connected = True
                self.mqtt.loop_forever()
            except Exception as e:
                sleep(1)

    def on_connect(self, client, data, flags, rc):
        self.mqtt.subscribe(self.SYS_TOPIC, 0)
        self.mqtt.subscribe('%s/#' % self.SERV_TOPIC, 0)

    def on_disconnect(self, client, userdata, rc):
        self.connected = False

    def on_message(self, client, data, msg):
        topic = msg.topic
        data = msg.payload.decode('utf-8')


if __name__ == '__main__':
    c = BricksClientAuth()
    c.run()
