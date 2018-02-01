#

from uplatform import json, UOBJ_DIR, PROP_VER


def base_properties(obj):
    return {'ver': PROP_VER, 'classname': obj.__class__.__name__, 'name': obj._name }


def config_apply(obj, proplist):
    for key, val in proplist.items():
        if "_"+key in obj.__dict__:
            obj.set_property("_"+key, val)


def config_get(obj):
    props = base_properties(obj)
    for key in str(obj.propertylist, 'utf-8').split(","):
        props[key] = getattr(obj, '_'+key)
    return props


def config_delete(namelist):
    from os import remove, listdir
    for id in namelist:
        try:
            remove('%s/%s.json' % (UOBJ_DIR, id))
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


def objects_files(skipfltr=''):
    from os import listdir
    flist = listdir(UOBJ_DIR)
    return [f.split('.')[0] for f in flist if f.split('.')[0] not in skipfltr]
