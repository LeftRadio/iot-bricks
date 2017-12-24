import gc
from uplatform import MICROPYTHON, MANGER_ID, MQTT_ESP_ID
from mqtt import MQTTClient
from base import objects_group
from actuators import Actuator
from sensors import DigitalInput, LM75, SHT21
from scenaries import UserTimer, Thermostat


class ObjectManager(object):

    propertylist = b'binds,interval'
    _commands = b'set,get,save,new,delete,datetime,ramfree,reset,sensors,actuators,scenaries'

    def __init__(self, name):
        self._classname = self.__class__.__name__
        self._name = name
        self._objects = {}
        self._binds = {}
        self._wlan_sta_state = False
        from uplatform import Timer
        self._gl_timer = Timer(-1)
        del(Timer)
        import machine
        self._datetime = None
        del(machine)
        self._interval = 1
        self.configured = False

    def set_property(self, attr, value):
        setattr(self, attr, value)
        if attr == '_binds':
            self.sync_binded_objects()

    def timer_init(self):
        self._gl_timer.deinit()
        self._gl_timer.init(
            period=int(self._interval*1000), callback=self.update)

    def update(self, *args, **kwargs):
        import time
        seconds = time.time()
        del(time)
        if MICROPYTHON:
            self._gl_timer.deinit()
            from network import WLAN, STA_IF
            wl = WLAN(STA_IF)
            if not wl.isconnected() or self._objects[MQTT_ESP_ID].state == b'server_lost':
                import machine
                machine.reset()
            del(wl)
            gc.collect()
            for obj in list(self._objects.values()):
                obj.update(interval=self._interval, seconds=seconds)
                gc.collect()
            self.timer_init()

    # --- commands methods ----------------------------------------------------

    def new_object(self, **kwargs):
        name = kwargs['name']
        classname = kwargs['classname']
        if gc.mem_free() < 3500:
            raise KeyError('no more memory')
        self._objects[name] = globals()[classname](**kwargs)
        self._objects[name].init()

    def delete_object(self, data):
        from config import config_delete
        if data == 'all':
            namelist = [k for k in self._objects.keys() if k != MQTT_ESP_ID]
            self._binds = {}
        else:
            namelist = data.split(',')
        [ self._objects.pop(n) for n in namelist ]
        config_delete(namelist)

    def sync_binded_objects(self):
        from config import config_get, save
        intents = ','.join(list(self._binds.values()))
        for obj in self._objects.values():
            if '_binded' not in obj.__dict__:
                continue
            if obj._name in intents:
                if obj._binded:
                    continue
                obj._binded = True
            elif obj._binded:
                obj._binded = False
            else:
                continue
            save(obj._name, config_get(obj))

    # --- callbacks -----------------------------------------------------------

    def objects_update_callback(self, sender, key, **kwargs):
        for src, recivers in self._binds.items():
            if sender._name != src or type(recivers) != str:
                continue
            for recv in recivers.split(','):
                try:
                    self._objects[recv].update_slot(sender, key, **kwargs)
                except Exception:
                    pass
        group = ''
        for k, v in objects_group.items():
            if sender.__class__.__name__ in v:
                group = k
                break
        self._objects[MQTT_ESP_ID].publish( group+'/'+sender._name, kwargs )

    def mqtt_recive_callback(self, recivername, command, data):
        reciver = None
        if recivername == self._name:
            reciver = self
        elif recivername in self._objects.keys():
            reciver = self._objects[recivername]
        else:
            return

        res_data = 'OK'

        try:
            cmdb = bytes(command, 'utf-8')
            assert cmdb in ObjectManager._commands

            if cmdb == b'set':
                from config import config_apply
                config_apply( reciver, data )

            elif cmdb == b'get':
                from config import config_get
                res_data = config_get(reciver)

            elif cmdb == b'save':
                from config import config_get, save
                save(recivername, config_get(reciver))
                if reciver == self and data == 'all':
                    [save(k, config_get(v)) for k, v in self._objects.items()]

            elif reciver == self:
                if cmdb == b'new':
                    self.new_object(**data)

                elif cmdb == b'delete':
                    self.delete_object(data)

                elif cmdb == b'ramfree':
                    gc.collect()
                    res_data = {'ramfree': gc.mem_free()}

                elif cmdb == b'datetime':
                    if not data:
                        import time
                        res_data = {'datetime': time.localtime()}
                    else:
                        import machine
                        machine.RTC().datetime(tuple(data))

                elif cmdb == b'reset':
                    import machine
                    machine.reset()

                elif command in objects_group.keys():
                    res_data = { command: [] }
                    for k, v in self._objects.items():
                        if v.__class__.__name__ in objects_group[command]:
                            res_data[command].append(k)
            else:
                raise KeyError(b'command not supported')
        except AssertionError as e:
            return
        except KeyError as e:
            res_data = { 'KeyError': (str(e)).encode('utf-8') }

        self._objects[MQTT_ESP_ID].publish(recivername, res_data)


# -------------------------------------------------------------------------


def manager_load(manager):
    from config import config_apply, load, objects_files
    from base import BrickBase
    gc.collect()
    try:
        config_apply( manager, load(MANGER_ID) )
    except Exception:
        pass
    try:
        mqttconf = load(MQTT_ESP_ID)
    except Exception:
        mqttconf = {'classname': 'MQTTClient', 'name': MQTT_ESP_ID, 'server': '192.168.0.103', 'keepalive': 60}
    manager.new_object( **mqttconf )
    try:
        files = objects_files(skipfltr='%s,%s' % (MANGER_ID, MQTT_ESP_ID))
        for f in files:
            gc.collect()
            try:
                manager.new_object( **load(f) )
            except Exception:
                pass
    except AssertionError:
        pass

    BrickBase.update_cb = manager.objects_update_callback
    manager._objects[MQTT_ESP_ID].recived_cb = manager.mqtt_recive_callback
    del(BrickBase)

    manager.configured = True
    return manager


# -------------------------------------------------------------------------


manager = manager_load( ObjectManager(name=MANGER_ID) )
del(manager_load)

manager.sync_binded_objects()

if MICROPYTHON:
    manager.timer_init()
else:
    from time import sleep
    while 1:
        sleep(1)
        manager.update()
