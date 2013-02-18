from model.Transaction import Transaction
from model.Thing import Thing
from model.cache import Cache
from copy import deepcopy

GROUPDB = 'db_Group'
GROUP_THINGS_DEFAULT = {'members': {},
                        'join_requests': {},
                        'comments': []
                        }
GROUP_PERMISSIONS_DEFAULT = {'add_new_members': False,
                             'add_new_task' : False,
                             'edit_task' : False,
                             'modify_member_rights' : False,
                             'finish_own_task' : True,
                             'finish_member_tasks' : False,
                             'restore_own_task' : True,
                             'restore_member_task' : False,
                             }
GROUP_PERMISSIONS_OWNER = {x : True for x in GROUP_PERMISSIONS_DEFAULT}
class Group(object):
    key = None
    _properties = None
    _things = None
    _changed = []
    
    def __init__(self, name=None):
        object.__setattr__(self, '_properties' , {})
        object.__setattr__(self, '_things' , {})
        object.__setattr__(self, 'key' , None)
        object.__setattr__(self, '_changed', [])
        
        if name:
            cache = Cache().get(GROUPDB, name)
            if cache:
                self._properties, things, self.key = cache
                self._things.update(things)
            else:    
                self.by_name(name)
    

    def by_name(self, name):
        t = Transaction(GROUPDB).query(name = name)
        if len(t)==0:
            return None
        t = t[0]
        self.key = t.pop('__key__')
        self._properties = t
        self._things.update(Thing(self.key).get())
        Cache().set(GROUPDB, name, (self._properties, self._things, self.key))
        return self
        
    def new(self, name, owner):
        self.key = Transaction(GROUPDB).set(name = name, owner = owner)
        self._things = Thing(self.key).new(deepcopy(GROUP_THINGS_DEFAULT))
        (self._things['members'])[owner] = deepcopy(GROUP_PERMISSIONS_OWNER)
        self._properties = {'name':name, 'owner':owner}
        self.commit(True)
        return self
    
    def commit(self, Force = False):
        Transaction(GROUPDB).update(self.key, self._properties)
        Thing(self.key).set(self._things, self._changed, Force)
        Cache().set(GROUPDB, self._properties['name'], (self._properties, self._things, self.key))
        return self
    
    def get_all(self):
        """Returns all groups as tuple of dictionaries"""
        return Transaction(GROUPDB).query()
    
    def add_join_request(self, name, msg = ""):
        (self._things['join_requests'])[name] = msg
    
    def remove_join_request(self, name):
        (self._things['join_requests']).pop(name, None)
        
    def add_member(self, name, permissions = deepcopy(GROUP_PERMISSIONS_DEFAULT)):
        (self._things['members'])[name] = permissions
        
    def accept_join_request(self, name):
        self.remove_join_request(name)
        self.add_member(name)
         
    def obj(self):
        return self.key
    
    def __getattr__(self, name):
        if name in self._properties:
            return self._properties[name]
        elif name == 'key':
            return self.key
        elif name in self._things:
            return self._things[name]
        elif name in GROUP_THINGS_DEFAULT:
            self._things[name] = (deepcopy(GROUP_THINGS_DEFAULT))[name]
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
   