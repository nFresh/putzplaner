import hashlib
import random
import string
import logging
import re
import datetime

from google.appengine.api import memcache
from model.db_models import db_Group
hashlib.md5


STALE = 10*60

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PWD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
NUMBER_RE = re.compile(r"[1-9][0-9]*")
SECRET = "c6b7196fe28552e089ebf9afd88b50fb0ef929034e01585dce9f637facb303a3"
GROUP_RE = re.compile(r"[\w_-](?:[\w_ -]|%20){2,39}", flags=re.UNICODE)
TASK_RE = GROUP_RE

def valid_username(s):
    return USER_RE.match(s)

def valid_groupname(s):
    return GROUP_RE.match(s)

def valid_taskname(s):
    return TASK_RE.match(s)

def valid_password(s):
    return PWD_RE.match(s)

def valid_email(s):
    return EMAIL_RE.match(s)

def valid_number(s):
    return NUMBER_RE.match(s)

def validDate(y, m, d):
    try:
        res = datetime.datetime(int(y), int(m), int(d))
    except ValueError:
        res = None
        logging.error("HEREHERHERHER!")
    return res

def Datetime_Breakdown(d):
    return d.strftime('%d %m %Y').split()


def make_salt():
    return ''.join(random.choice(string.letters) for _ in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)

def secret_hash(s):
    return hashlib.sha256(s+SECRET).hexdigest()



class NoneResult(object): pass

def make_key(iden, *a, **kw):
    """
A helper function for making memcached-usable cache keys out of
arbitrary arguments. Hashes the arguments but leaves the `iden'
human-readable
""" 
    from model.Calendar import Calendar
    from model.Task import Task
    h = hashlib.md5()
    
    def _conv(s):
        if isinstance(s, str):
            return s
        elif isinstance(s, unicode):
            return s.encode('utf-8')
        elif isinstance(s, (tuple, list)):
            return ','.join(_conv(x) for x in s)
        elif isinstance(s, dict):
            return ','.join('%s:%s' % (_conv(k), _conv(v))
                            for (k, v) in sorted(s.iteritems()))
        elif isinstance(s, db_Group):
            return s.name
        elif isinstance(s, Calendar):
            return ''
        elif isinstance(s, Task):
            return ''
        else:
            return str(s)
    
    iden = _conv(iden)
    h.update(iden)
    h.update(_conv(a))
    h.update(_conv(kw))
    
    return '%s(%s)' % (iden, h.hexdigest())
     
        
def memoize(iden):
    def memoize_fn(fn):
        def _fn(*a, **kwargs):
            
            update = kwargs.pop('_update', False)
            key = make_key(iden, *a, **kwargs)
            
            logging.error(update)
            logging.error(key)

            res = None if update else memcache.get(key)
            if res is None:
                res = fn(*a, **kwargs)
                if res is None:
                    res = NoneResult
                memcache.set(key, res, STALE)
            
            if res == NoneResult:
                res = None
            return res
        return _fn
    return memoize_fn
                    
        
        
        
        
   

    
