
import threading
import time


class TimerBase(object):

    PERIODIC = 0x00

    def __init__(self, *args, **kwargs):
        pass

    def init(self, *args, **kwargs):
        pass

    def deinit(self):
        pass


class Timer(TimerBase):

    def __init__(self, *args, **kwargs):
        super(Timer, self).__init__(*args, **kwargs)
        self._sec = 0
        self.period = 1000
        self.run = False

    def _worker(self):
        while self.run is True:
            time.sleep(self.period/1000)
            self.callback()

    def init(self, *args, **kwargs):
        self.period = kwargs.get('period', self.period)
        self.callback = kwargs.get('callback', self._callback)
        self._sec = 0
        self.run = True
        self.t1 = threading.Thread( target=self._worker )
        self.t1.daemon = True
        self.t1.start()

    def deinit(self):
        super().deinit()
        self.run = False

    def reset(self):
        self._sec = 0

    def _callback(self):
        pass


# class GlobalTimer(TimerBase):
#     """docstring for GlobalTimer"""
#     def __init__(self, name, *args, **kwargs):
#         super(GlobalTimer, self).__init__(*args, **kwargs)
#         #
#         self.name = name
#         self.run = False
#         self.sec = 0
#         #
#         self.manager = None

#     def _worker(self):
#         while self.run is False:
#             time.sleep( self.period / 1000.0 )
#             self.sec += 1
#             self.callback(self, self.sec)

#     def init(self, *args, **kwargs):
#         self.manager = ObjectManager(name='manager')
#         self.manager.init()
#         t1 = threading.Thread( target=self._worker )
#         self.period = kwargs.get('period', 1000)
#         self.callback = kwargs.get('callback', self.workcallback)
#         self.sec = 0
#         t1.start()

#     def workcallback(self, obj, sec):
#         self.manager.update()
