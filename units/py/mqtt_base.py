
import ustruct as struct
import usocket as socket
from bmdns import get_server_ip as get_localserver


class MQTTClientBase(object):
    '''docstring for MQTTClientBase'''
    def __init__(self, **kwargs):
        self._sock = None
        self._pid = 0
        self._lw_topic = None
        self._lw_msg = None
        self._lw_qos = 0
        self._lw_retain = False

        self._alt_settings = kwargs.get('alt_settings', [])
        self._alt_index = kwargs.get('alt_index', 0)

        self._keepalive = kwargs.get('keepalive', 60)
        self._ssl = kwargs.get('ssl', False)
        self._ssl_params = kwargs.get('ssl_params', {})

        self.connected_cb = None
        self.recived_cb = None
        self.disconnect_cb = None

    def _send_str(self, s):
        out = bytearray()
        out.extend(struct.pack('!H', len(s)))
        out.extend(bytes(s, 'utf-8'))
        self._sock.write(out)

    def _recive(self, lenb):
        res = self._sock.read(lenb)
        if res is None:
            raise OSError(10035)
        return res

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self._recive(1)[0]
            n |= (b & 0x7f) << sh
            if not b & 0x80:
                return n
            sh += 7

    def _recive_msg(self, topic, msg):
        if self.recived_cb is not None:
            self.recived_cb(str(topic, 'utf-8'), str(msg, 'utf-8'))

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self._lw_topic = topic
        self._lw_msg = msg
        self._lw_qos = qos
        self._lw_retain = retain

    def connect(self, timeout=1, clean_session=True):
        assert len(self._alt_settings)
        serv, port, user, pswd = self._alt_settings[self._alt_index].split(',')
        if serv.endswith('.local'):
            serv = get_localserver(serv, timeout=timeout)
            assert serv is not None
        addr_info = socket.getaddrinfo(serv, int(port))[0][-1]
        self._sock = socket.socket()
        self._sock.settimeout(timeout)
        self._sock.connect(addr_info)
        if self._ssl:
            import ussl
            self._sock = ussl.wrap_socket(self._sock, **self._ssl_params)
        msg = bytearray(b'\x10\x00\x00\x04MQTT\x04\x02\x00\x00')
        msg[1] = 10 + 2 + len(self._name)
        msg[9] = clean_session << 1
        if user:
            msg[1] += 2 + len(user) + 2 + len(pswd)
            msg[9] |= (0x03) << 6
        if self._keepalive:
            assert self._keepalive < 65536
            msg[10] |= self._keepalive >> 8
            msg[11] |= self._keepalive & 0x00FF
        if self._lw_topic:
            msg[1] += 2 + len(self._lw_topic) + 2 + len(self._lw_msg)
            msg[9] |= 0x4 | (self._lw_qos & 0x1) << 3 | (self._lw_qos & 0x2) << 3
            msg[9] |= self._lw_retain << 5
        self._sock.write(msg)
        self._send_str(self._name)
        if self._lw_topic:
            self._send_str(self._lw_topic)
            self._send_str(self._lw_msg)
        if user:
            self._send_str(user)
            self._send_str(pswd)
        resp = self._recive(4)
        if resp is None or not len(resp):
            raise OSError(-1)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise OSError(resp[3])
        if self.connected_cb is not None:
            self.connected_cb(resp[2] & 0x01, addr_info)
        return (resp[2] & 0x01, addr_info)

    def disconnect(self):
        try:
            self._sock.write(b'')
        except Exception:
            pass
        try:
            self._sock.close()
        except Exception:
            pass
        if self.disconnect_cb:
            self.disconnect_cb()

    def ping(self):
        try:
            self._sock.write(b' ')
        except OSError:
            pass

    def publish(self, topic, msg, retain=0, qos=0):
        if qos == 2:
            assert 0
        pkt = bytearray(b'\x30\x00\x00')
        pkt[0] |= qos << 1 | retain
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        assert sz <= 16383
        pkt[1] = (sz & 0x7f) | 0x80
        pkt[2] = sz >> 7
        self._sock.write(pkt)
        self._send_str(topic)
        if qos > 0:
            self._pid += 1
            pid = self._pid
            buf = bytearray([0x00, 0x00])
            struct.pack_into('!H', buf, 0, pid)
            self._sock.write(buf)
        self._sock.write(msg)
        if qos == 1:
            while 1:
                op = self.wait_msg()
                if op == 0x40:
                    sz = self._recive(1)
                    assert sz == b''
                    rcv_pid = self._recive(2)
                    rcv_pid = rcv_pid[0] << 8 | rcv_pid[1]
                    if pid == rcv_pid:
                        break

    def subscribe(self, topic, qos=0):
        pkt = bytearray([0x82, 0x00, 0x00, 0x00])
        self._pid += 1
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, self._pid)
        self._sock.write(pkt)
        self._send_str(topic)
        self._sock.write(qos.to_bytes(1, "little"))
        while 1:
            op = self.wait_msg()
            if op == 0x90:
                resp = self._sock.read(4)
                assert resp[1] == pkt[2] and resp[2] == pkt[3]
                if resp[3] == 0x80:
                    raise OSError(resp[3])
                return

    def wait_msg(self):
        res = self._recive(1)
        self._sock.setblocking(True)
        if res == b'':
            raise OSError(-1)
        if res == b'\xd0':  # PINGRESP
            sz = self._recive(1)[0]
            assert sz == 0
            return None
        op = res[0]
        if op & 0xf0 != 0x30:
            return op
        sz = self._recv_len()
        topic_len = self._recive(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = self._recive(topic_len)
        sz -= topic_len + 2
        if op & 6:
            pid = self._recive(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        msg = self._recive(sz)
        if op & 6 == 2:
            pkt = bytearray([0x40, 0x02, 0x00, 0x00])
            struct.pack_into('!H', pkt, 2, pid)
            self._sock.write(pkt)
        elif op & 6 == 4:
            assert 0
        self._recive_msg(topic, msg)
        return op

    def check_msg(self):
        self._sock.setblocking(False)
        return self.wait_msg()
