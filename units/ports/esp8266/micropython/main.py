
from uplatform import UOBJ_DIR


def create_data_dir():
    import os
    from uplatform import UOBJ_DIR
    if UOBJ_DIR not in os.listdir():
        os.mkdir(UOBJ_DIR)
    del(os)
    del(UOBJ_DIR)


def start_delay():
    from time import time
    for x in range(1, 50000):
        pass
    del(time)


create_data_dir()
start_delay()
del(create_data_dir)
del(start_delay)


import user_main
