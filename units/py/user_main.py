import gc
import machine
import time

from defaults import MANGER_NAME_ID, WLAN_NAME_ID, MQTT_NAME_ID

from uplatform import PLATFORM
from uplatform import Timer

from config import save, configs_delete, load, objects_files

from wlan import WLAN_STA_Manager
from mqtt import MQTTClient

import bricks
from actuators import DigitalOut
from sensors import DigitalInput, LM75, SHT21
from scenaries import UserTimer, Regulator


# -------------------------------------------------------------------------

def bricks_objects_native_cb(sender, data):
    """ Wrap callback for native Bricks objects,
        FatalException if redefine to manager.objects_update_callback
    """
    manager.objects_update_callback(sender, data)


bricks.set_callback(bricks_objects_native_cb)


# -------------------------------------------------------------------------

class ObjectManager(object):

    propertylist = b'binds,interval'
    commands = b'set,get,save,new,delete,datetime,ramfree,reset,objects,' + bytes(','.join(bricks.groups()), 'utf-8')

    def __init__(self):
        # default settings
        self.classname = self.__class__.__name__
        self.name = MANGER_NAME_ID
        self.objects = {}
        self.binds = {}
        self.datetime = None
        self.interval = 1
        self._gl_timer = Timer(-1)

        # create 'static' WLAN/MQTT objects
        self.objects[WLAN_NAME_ID] = WLAN_STA_Manager()
        self.objects[MQTT_NAME_ID] = MQTTClient()

        # list stored settings json files for objects
        files = objects_files()
        # try load stored settings for itself
        try:
            f = files.pop(files.index(self.name))
            self.properties( **load(f) )
        except Exception:
            pass

        # load settings and create objects
        for f in files:
            try:
                self.new_object( **load(f) )
            except Exception:
                pass

        # set WLAN and MQTT objects specefic callbacks
        self.objects[MQTT_NAME_ID].recived_cb = self.mqtt_recive_callback
        self.objects[MQTT_NAME_ID].state_callback = self.mqtt_state_callback
        self.objects[WLAN_NAME_ID].status_cb = self.wlan_status_callback

        # finally update/sync binded objects
        self.sync_binded_objects(self.binds)

    def set_property(self, key, value):
        if key[0] == '_':
            return
        elif key == 'binds':
            self.sync_binded_objects(value)
        setattr(self, key, value)

    def properties(self, **kwargs):
        if not len(kwargs):
            return {
                'classname': self.__class__.__name__,
                'name': self.name,
                'binds': self.binds,
                'interval': self.interval
            }
        for k, v in kwargs.items():
            self.set_property(k, v)

    def timer_init(self):
        self._gl_timer.deinit()
        if self.interval < 0.25:
            self.interval = 0.25
        self._gl_timer.init(
            period=int(self.interval*1000), callback=self.update)

    def update(self, timer):
        self._gl_timer.deinit()
        #
        # machine.freq(160000000)
        now = time.ticks_ms()
        seconds = time.time()
        for obj in self.objects.values():
            obj.update(seconds, self.interval)
            gc.collect()
        print('update ms: ', time.ticks_ms() - now)
        # machine.freq(80000000)
        #
        self.timer_init()

    # --- commands methods ----------------------------------------------------

    def new_object(self, **kwargs):
        name = kwargs['name']
        classname = kwargs.pop('classname')
        gc.collect()
        if gc.mem_free() < 4000:
            raise MemoryError
        self.objects[name] = globals()[classname](**kwargs)
        self.objects[name].init()

    def delete_object(self, data):
        if data == 'all':
            namelist = objects_files()
            self.objects.clear()
        else:
            namelist = data.split(',')
            [ self.objects.pop(n) for n in namelist ]
        configs_delete(namelist)

    def sync_binded_objects(self, binds):

        intents = ';'.join(list(binds.values()))

        for obj in self.objects.values():
            p = obj.properties()
            if 'binded' not in p:
                continue
            name = obj.name()
            if name in intents:
                if p['binded']:
                    continue
                p['binded'] = True
            elif p['binded']:
                p['binded'] = False
            else:
                continue
            save(obj.name(), p)

    # --- callbacks -----------------------------------------------------------

    def objects_update_callback(self, sender, data):
        #
        name = sender.name()

        for src, recivers in self.binds.items():
            if name != src:
                continue
            for recv in recivers.split(','):
                try:
                    self.objects[recv].update_slot(sender, data)
                except Exception as e:
                    pass
                gc.collect()

        self.objects[MQTT_NAME_ID].publish( '%s/%s' % (sender.group(), name), data )

    def mqtt_recive_callback(self, recivername, command, data):

        if recivername == self.name:
            reciver = self
        elif recivername in self.objects.keys():
            reciver = self.objects[recivername]
        else:
            return

        res_data = b'OK'

        try:
            cmdb = bytes(command, 'utf-8')
            assert cmdb in ObjectManager.commands

            if cmdb == b'set':
                reciver.properties(**data)

            elif cmdb == b'get':
                res_data = reciver.properties()

            elif cmdb == b'save':
                save(recivername, reciver.properties())
                if reciver == self and data == 'all':
                    for k, v in self.objects.items():
                        save(k, v.properties())

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
                        machine.RTC().datetime(tuple(data))

                elif cmdb == b'objects':
                    res_data = { command: list(self.objects.keys()) }

                elif command in bricks.groups():
                    objlist = [ k for k,v in self.objects.items() if v.group() == command ]
                    res_data = { command: objlist }

                elif cmdb == b'reset':
                    machine.reset()

            else:
                raise KeyError(b'command not supported')
        except AssertionError as e:
            return
        except KeyError as e:
            res_data = { 'KeyError': (str(e)).encode('utf-8') }

        self.objects[MQTT_NAME_ID].publish(recivername, res_data)

    def mqtt_state_callback(self, state):
        mqtt = self.objects[MQTT_NAME_ID]
        print(b'mqtt_state_callback: ', mqtt.alt_settings[mqtt.alt_index], state)
        if state == b'server_lost':
            # if wlan object status is STAT_GOT_IP
            if self.objects[WLAN_NAME_ID].itf.status() == 5:
                mqtt.set_property('alt_index', mqtt.alt_index + 1)
                mqtt.state = b'reset'

    def wlan_status_callback(self, status):
        wlan = self.objects[WLAN_NAME_ID]
        mqtt = self.objects[MQTT_NAME_ID]
        print(b'wlan_status_callback: ', status)
        if status < 5:
            if status > 1:
                wlan.set_property('alt_index', wlan.alt_index + 1)
            mqtt.state = b'server_lost'
        elif status == 5:
            mqtt.state = b'reset'


# -------------------------------------------------------------------------


manager = ObjectManager()

if PLATFORM == b'mpy':
    manager.timer_init()
else:
    from time import sleep
    while True:
        sleep(manager.interval)
        manager.update()
