
import os
from uplatform import json, UOBJ_DIR


def configs_delete(namelist):
    for id in namelist:
        try:
            os.remove('%s/%s.json' % (UOBJ_DIR, id))
        except Exception:
            pass


def save(id, data):
    with open('%s/%s.json' % (UOBJ_DIR, id), 'w') as f:
        data = json.dumps( data )
        f.write(data)


def load(id):
    with open('%s/%s.json' % (UOBJ_DIR, id), 'r') as f:
        data = f.read()
        data = json.loads( data )
    return data


def objects_files():
    try:
        flist = os.listdir(UOBJ_DIR)
        return [f.split('.')[0] for f in flist]
    except Exception:
        return []

