from model.Transaction import Transaction
from model.Thing import Thing
from model.cache import Cache

from model.cache import NoneResult
COMMENTDB = 'db_Comments'


class Comment(object):
    
    def get(self, parent, update = False, **kwargs):
        res = Cache.get(COMMENTDB, parent, **kwargs)
        if not res or update:
            res = Transaction(COMMENTDB).query(parent = parent, **kwargs)
            if res == None:
                res = NoneResult
            Cache.set(COMMENTDB, parent, res,**kwargs)
        return None if res == NoneResult else res
    
    def set(self, parent, text, source):
        """parent = target-key or entity source = Name"""
        Transaction(COMMENTDB).set(parent = parent, text = text, source = source )
        self.get(parent, True, order = "-datetime")
        
        