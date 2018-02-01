

def get_server_ip(name, mcast_group='224.0.0.251', port=5353, timeout=1):

    import ustruct as struct
    import usocket as socket

    # get server name without [ .local ]
    name = name.split('.')[0]
    # mDNS type A request
    pkg = bytearray( b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00')
    pkg.extend( struct.pack( 'B', len(name) ) )
    pkg.extend( bytes(name, 'utf-8') )
    pkg.extend( b'\x05local' )
    pkg.extend( b'\x00\x00\x01\x00\x01' )
    # create socket
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    #
    sock.bind( ('0.0.0.0', port) )
    # respond server ip
    server_ip = None
    #
    try:
        # !!! request IS COMPATIBLE with mDNS specs !!!
        # !!! mDNS service started on server !!!
        sock.sendto( pkg, (mcast_group, port) )

        # !!! respond NOT COMPATIBLE with mDNS specs !!!
        # !!! mDNS service not started on ESP !!!
        m = sock.recvfrom( 128 )

        # parse respond from iot-bricks-server user deamon
        # deamon is polled mDNS request and respond:
        # pack = [ 0x84, 0x48, 0x88, 0x44 ]
        # pack.extend( server_name_len_byte )
        # pack.extend( server_name_str_utf_8 )
        # pack.extend( server_addr_len_byte )
        # pack.extend( server_addr_str_utf_8 )
        pl = m[0]
        if pl[0] == 0x84 and pl[1] == 0x48 and pl[2] == 0x88 and pl[3] == 0x44:
            nm_len = pl[4]
            nm = str( pl[5:(5+nm_len)], 'utf-8')
            nm = nm.split('.')[0]
            if nm == name:
                server_ip = m[1][0]
    except Exception:
        pass
    # close socket
    try:
        sock.close()
    except Exception:
        pass

    del(sock)
    del(struct)
    del(socket)

    return server_ip
