

class BrickBase(object):

    update_cb = None

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.enable = kwargs.get('enable', False)
        self.binded = kwargs.get('binded', False)
        if self.binded:
            self.out_state = False
        else:
            self.out_state = kwargs.get('out_state', False)

    def set_property(self, key, value):
        if key[0] == '_':
            return
        setattr(self, key, value)

    def init(self):
        pass

    def update_slot(self, sender, data):
        pass
