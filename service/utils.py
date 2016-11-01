import os
from array import array

colors = range(2,10) + range(30,50)

def env_var(key, default=None):
    """Retrieves env vars and makes Python boolean replacements"""
    val = os.environ.get(key, default)
    if val == 'True':
        val = True
    elif val == 'False':
        val = False
    return val


def root_data():
    return env_var(
        'ROOT_DATA',
        os.path.join(
            os.path.dirname(os.path.abspath(os.path.join(__file__, '..'))),
            'data')
    )


def serie(s, f=float):
    if not s:
        return []
    return map(lambda arr: map(f, arr),
               map(lambda s: s.split(','), s.split(";")))


def fserie(s):
    return map(lambda a: array('f', a), serie(s))
