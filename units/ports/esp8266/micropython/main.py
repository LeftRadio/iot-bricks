

def create_data_dir():
    import os
    from uplatform import DATADIR
    if DATADIR not in os.listdir():
        os.mkdir(DATADIR)
    del(os)
    del(DATADIR)


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
