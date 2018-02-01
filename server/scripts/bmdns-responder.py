
from time import sleep
import struct
import socket
import dpkt, dpkt.dns

#join the multicast group
# mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
# print([int(b) for b in socket.inet_aton(MCAST_GRP)] , [int(b) for b in mreq])
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

UDP_IP = "0.0.0.0"
UDP_PORT = 5353
MCAST_GRP = '224.0.0.251'

sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind( (UDP_IP, UDP_PORT) )
sock.settimeout(0.25)

while 1:
    try:
        d = sock.recvfrom( 1024 )
        dns = dpkt.dns.DNS(d[0])

        if len(dns.qd) > 0:
            nm = dns.qd[0].name
            print('recive mDNS qd', nm, d[1] )
            if nm == socket.gethostname() + '.local':
                addr = socket.getaddrinfo('127.0.0.1', 5353)[0][-1]
                rd = bytearray(b'\x84\x48\x88\x44')
                rd.extend( struct.pack('B', len(nm)) )
                rd.extend( bytearray(bytes(nm, 'utf-8')) )
                rd.extend( struct.pack('B', len(addr[0])) )
                rd.extend( bytearray(bytes(addr[0], 'utf-8')) )
                rd.extend( bytearray(128-len(rd)))
                sock.sendto( rd, d[1] )

    except Exception as e:
        if 'timed out' not in str(e):
            print('ex: ', str(e))
        pass
