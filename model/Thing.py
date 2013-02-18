import pickle
from model.Transaction import Transaction
from copy import deepcopy

THINGDB = 'db_Thing'
DEFAULT_THING = {'test': 1}

class Thing(object):
    parent_key = None
    
    def __init__(self, parent_key):
        self.parent_key = parent_key    
    
    def get(self):
        things = Transaction(THINGDB).query(parent = self.parent_key)
        res = {}
        for thing in things:
            res[thing['name']] = pickle.loads(thing['value'])
        return res
    
    def set(self, things, changed, Force=False):
        """Commits all changes to the DB, if Force = True, everything will be commited"""
        for thing in things:
            if thing in changed or Force:
                Transaction(THINGDB).set(parent = self.parent_key, key_name = thing, name = thing, value = pickle.dumps(things[thing]))
        return True
    
    def new(self, extra_defaults = None):
        things = deepcopy(DEFAULT_THING)
        if extra_defaults:
            for extra in extra_defaults:
                things[extra] = extra_defaults[extra]
        self.set(things, things.keys())
        return things
            