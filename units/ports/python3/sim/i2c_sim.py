
from random import randrange


class I2C(object):
    """docstring for I2C"""
    def __init__(self, *args, **kwargs):
        pass

    def readfrom(self, addr, rlen):
        x = randrange(0, stop=+25, step=1, _int=int)
        return bytearray( [x for n in range(rlen)] )

    def writeto(self, data):
        return len(data)
