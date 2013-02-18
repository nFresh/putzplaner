from model.Transaction import Transaction
from model.Thing import Thing
from model.cache import Cache


TASKDB = 'db_Task'

TASK_THINGS_DEFAULT = { 'testtask' : 1,
                        'intervall' : 7,
                        }
                       
class Task(object):
    key = None
    _properties = None
    _things = None
    _changed = []
    _parent = None
    
    def __init__(self, parent = None, name=None):
        object.__setattr__(self, '_properties' , {})
        object.__setattr__(self, '_things' , {})
        object.__setattr__(self, 'key' , None)
        object.__setattr__(self, '_changed', [])
        object.__setattr__(self, '_parent', [])
        
        if name and parent:
            self._parent = parent
            cache = Cache().get(TASKDB, str(parent) + name)
            if cache:
                self._properties, things, self.key, self._parent = cache
                self._things.update(things)
            else:    
                self.by_keyname_and_parent(name, parent)


       
    def by_keyname_and_parent(self, key_name, parent):
        t = (Transaction(TASKDB).by_key_name_and_parent(key_name, parent))[0]
        self.key = t.pop('__key__')
        self._properties = t
        self._things.update(Thing(self.key).get())
        Cache().set(TASKDB, str(parent) + key_name, (self._properties, self._things, self.key, self._parent))
        return self
    
    def new(self, parent, name, description, **kwargs ):
        self.key = Transaction(TASKDB).set(key_name = name, parent = parent, name = name, description = description)
        self._things = Thing(self.key).new(TASK_THINGS_DEFAULT)
        for kw in kwargs:
            self._things[kw] = kwargs[kw]
        self._properties = {'name': name, 'description': description}
        self._parent = parent
        self.commit(True)
    
    def commit(self, Force = False):
        Transaction(TASKDB).update(self.key, self._properties)
        Thing(self.key).set(self._things, self._changed, Force)
        Cache().set(TASKDB, str(self._parent) + self._properties['name'], (self._properties, self._things, self.key, self._parent))
    
    @staticmethod
    def all(parent):
        return Transaction(TASKDB).query(parent = parent)
    
    
    def __getattr__(self, name):
        if name in self._properties:
            return self._properties[name]
        elif name == 'key':
            return self.key
        elif name in self._things:
            return self._things[name]
        elif name in TASK_THINGS_DEFAULT:
            self._things[name] = TASK_THINGS_DEFAULT[name]
            self._changed.append(name)
            return self._things[name]
        return None
    
    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        elif name in self._properties:
            setattr(self._properties, name, value) 
        else:
            setattr(self._things, name, value)
            self._changed.append(name)
    