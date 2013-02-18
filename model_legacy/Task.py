from model.Transaction import Transaction
from model.Thing import Thing
from model.db_models import db_Task
from lib.utils import memoize
import logging
TASKDB = 'db_Task'

TASK_THINGS_DEFAULT = { 'testtask' : 1,
                        'intervall' : 7,
                       }

class Task(object):
    _task = None
    _thing = None
   
    def __init__(self):
        object.__setattr__(self, '_task' , None)
        object.__setattr__(self, '_thing' , None)
        
    def new(self, parent, **kwargs):
        name = kwargs.pop('name')
        description = kwargs.pop('description')
        task = Transaction(TASKDB).set_new(parent,key_name = name, name = name, description = description)
        task.commit()
        thing = Thing(task.obj())
        for t in TASK_THINGS_DEFAULT:
            setattr(thing, t, TASK_THINGS_DEFAULT[t])
        for kw in kwargs:
            setattr(thing, kw, kwargs[kw])
        thing.commit()
        self._task = task
        self._thing = thing
        self.all(parent, _update = True)
        return self
    
    def __by_name_and_parent(self, name, parent):
        logging.error(parent)
        logging.error(name)
        task = Transaction(TASKDB).query_by_property_simple(parent = parent, name = name)
        if not task.obj():
            return (None, None)
        thing = Thing(task.obj())
        return (task, thing)
    
    def by_name_and_parent(self, name, parent):
        """ Needs Group as parent """
        self._task, self._thing = self.__by_name_and_parent(name, parent)
        if self._task:
            return self
        return None
    
    @memoize('Task_all')
    def all(self, parent):
        t = Transaction(TASKDB).query_by_ancestor(parent)
        if t:
            return t.get_all()
        return []
    
    def commit(self):
        self._task.commit()
        self._thing.commit()
    
    def __getattr__(self, name):
        if name in db_Task.properties():
            return getattr(self._task, name)
        else:
            res =  getattr(self._thing, name)
            if not res and name in TASK_THINGS_DEFAULT:
                return TASK_THINGS_DEFAULT[name]
            return res
    
    def __setattr__(self, name, value):    
        if name in self.__dict__:
            self.__dict__[name] = value
        elif name in db_Task.properties():
            setattr(self._task, name, value)
        else:
            setattr(self._thing, name, value)    
        
        