

class Pin(object):

    IN = 0x00
    OUT = 0x01

    def __init__(self, indx=0, mode=0, value=0):
        self.indx = indx
        self.state = 0
        self.enable = False

    def low(self):
        self.state = 0

    def high(self):
        self.state = 1

    def value(self):
        return self.state
