
from uplatform import unique_id


MANGER_NAME_ID = 'manager'


WLAN_NAME_ID = 'wlan'
WLAN_SETTINGS = [
    'IOT-BRICKS-CONFIG,1234root1234',
    'NeilLab,statemachine-UX7',
]


MQTT_NAME_ID = 'iot_brick_esp_' + '_'.join([str(b) for b in unique_id()])
MQTT_SETTINGS = [
    'iot-bricks-server.local,8883,admin,admin,ssl,certnone,30',
    'iot-bricks-server.local,1883,admin,admin,,,30',
    'Aspire-4315.local,1883,test,test,,,300',
]


MODULE_SERIAL_HASH = b'f4b0d91d26a82aa23e0bbf82fcbccecb6103a932481b4ed35099be3eecf9c399'
