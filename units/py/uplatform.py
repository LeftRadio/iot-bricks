

PLATFORM = b'mpy'


if PLATFORM == b'mpy':
    from micropython import const
    import ujson as json
    from machine import Timer
    from machine import Pin, Signal
    from machine import I2C
    from machine import ADC
    from machine import unique_id
    import ustruct as struct
    import usocket as socket
    import utime
    from network import WLAN, STA_IF, AP_IF
    from network import ( STAT_IDLE, STAT_CONNECTING, STAT_WRONG_PASSWORD,
                          STAT_NO_AP_FOUND, STAT_CONNECT_FAIL, STAT_GOT_IP )
    UOBJ_DIR = 'data'

elif PLATFORM == b'python3':
    const = lambda x: int(x)
    import json
    from sim.timer_sim import Timer
    from sim.pin_sim import Pin
    from sim.i2c_sim import I2C
    unique_id = lambda: [32, 123, 2, 1]
    from random import randrange
    import struct
    import socket
    import time as utime
    from sim.wlan_sim import WLAN, STA_IF
    from sim.wlan_sim import ( STAT_IDLE, STAT_CONNECTING, STAT_WRONG_PASSWORD,
                               STAT_NO_AP_FOUND, STAT_CONNECT_FAIL, STAT_GOT_IP )
    import os
    UOBJ_DIR = os.path.abspath(os.path.dirname(__file__)+'/data')

else:
    raise Exception(b'Platform [ %b ] invalid!' % PLATFORM )


#
PROP_VER = const(102)
#
MANGER_ID = 'manager'
WLAN_ID = 'wlan'
MQTT_ESP_ID = 'iot_brick_esp_' + '.'.join([str(b) for b in unique_id()])
