

PLATFORM = b'mpy'


if PLATFORM == b'mpy':
    from micropython import const
    import ujson as json
    from machine import Timer
    from machine import Pin
    from machine import I2C
    from machine import unique_id
    import ustruct as struct
    import usocket as socket
    import utime
    UOBJ_DIR = 'data'

elif PLATFORM == b'python3':
    const = lambda x: int(x)
    import json
    from py3_hw_sim.timer_sim import Timer
    from py3_hw_sim.pin_sim import Pin
    from py3_hw_sim.i2c_sim import I2C
    unique_id = lambda: [32, 123, 2, 1]
    from random import randrange
    import struct
    import socket
    import time as utime
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
