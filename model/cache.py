from google.appengine.api import memcache
from lib.utils import make_key

STALE = 10*60

class NoneResult(): pass

CACHE = {}
CACHE_KEYS =[]

class Cache(object):
    """VERY, VERY, VERY simple Cache class"""
    
    @staticmethod
    def get(kind, key, **kwargs):
        hkey = make_key(kind, key, **kwargs)
        if hkey in CACHE:
            return CACHE[hkey]
        res = memcache.get(hkey)
        return res
    
    @staticmethod
    def set(kind, key, value, **kwargs):
        hkey = make_key(kind, key, **kwargs)
        if len(CACHE) >= 100:           #
            t = CACHE_KEYS[0]
            del CACHE_KEYS[0]
            CACHE.pop(t, None)
        CACHE[hkey] = value
        if hkey in CACHE_KEYS:
            del CACHE_KEYS[CACHE_KEYS.index(hkey)]
        CACHE_KEYS.append(hkey)
        memcache.set(hkey, value, STALE)
        return True    
    