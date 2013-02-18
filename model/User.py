from lib.utils import make_pw_hash
from model.Transaction import Transaction
from model.Thing import Thing
from model.cache import Cache
from copy import deepcopy
import logging

USERDB = 'db_User'
USER_THINGS_DEFAULT = {'groups': {},
                       'isAdmin': False,
                       }

class User(object):
    key = None
    _properties = None
    _things = None
    _changed = []
    
    def __init__(self, name=None):
        object.__setattr__(self, '_properties' , {})
        object.__setattr__(self, '_things' , deepcopy(USER_THINGS_DEFAULT))
        object.__setattr__(self, 'key' , None)
        object.__setattr__(self, '_changed', [])
        
        if name:
            cache = Cache().get(USERDB, name)
            if cache:
                self._properties, things, self.key = cache
                self._things.update(things)
            else:    
                self.by_name(name)        
        
        
    def by_name(self, name):
        t = (Transaction(USERDB).query(name = name))
        if len(t) == 0:
            return None
        t = t[0]
        self.key = t.pop('__key__')
        self._properties = t
        self._things.update(Thing(self.key).get())
        Cache().set(USERDB, name, (self._properties, self._things, self.key))
        return self
        
    def new(self, name, pw, email):
        password = make_pw_hash(name, pw)
        self.key = Transaction(USERDB).set(name = name, password = password, email = email)
        self._things = Thing(self.key).new(deepcopy(USER_THINGS_DEFAULT))
        self._properties = {'name':name, 'password':password, 'email':email}
        return self
    
    def commit(self):
        Transaction(USERDB).update(self.key, self._properties)
        Thing(self.key).set(self._things, self._changed)
        Cache().set(USERDB, self._properties['name'], (self._properties, self._things, self.key))
        return self
    
    def validate_pw(self, pw):
        pwsalt = self.password.split('|')[1]
        return make_pw_hash(self.name, pw, pwsalt) == self.password
    
    def add_grp(self, groupname):
        (self._things['groups'])[groupname] = ''
        self._changed.append('groups')
        return self
    
        
    def __getattr__(self, name):
        if name in self._properties:
            return self._properties[name]
        elif name == 'key':
            return self.key
        elif name in self._things:
            return self._things[name]
        elif name in USER_THINGS_DEFAULT:
            self._things[name] = (deepcopy(USER_THINGS_DEFAULT))[name]
            self._changed.append(name)
            return self._things[name]
        return None
    
    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        elif name in self._properties:
            self.__dict__['_properties'][name] = value
        else:
            self.__dict__['_things'][name] = value
            self._changed.append(name)
            
            