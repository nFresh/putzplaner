import model.db_models
import pickle
import logging

from google.appengine.ext import db

def iterable(a):
    try:
        (x for x in a)
        return True
    except TypeError:
        return False


class Transaction(object):
    _model = None
    _obj = None
    _is_Thing = False
    _single_entry = False
    
    def __init__(self, kind, is_Thing = False):
        object.__setattr__(self, '_model' , db.class_for_kind(kind))
        object.__setattr__(self, '_is_Thing', is_Thing)
        object.__setattr__(self, '_obj', None)
        object.__setattr__(self, '_single_entry', False)
    
    def query_by_ancestor(self, parent):
        if parent:
            obj = self._model.all()
            self._obj = obj.ancestor(parent)
            self.make_query()
            if not self._obj:
                return None
            return self
        return None
    
    def query_by_key(self, key):
        self._obj = self._model.all().filter('__key__ =', key)
        self._make_query()
        return self
        
    def query_by_property_simple(self, **kwargs):
        """takes list of kewords + values and queries _model db"""
        obj = self._model.all()
        order = kwargs.pop('order', None)
        parent = kwargs.pop('parent', None)
        key_name = kwargs.pop('key_name', None)
        if key_name and parent:
            obj = self._model.get_by_key_name(key_name, parent)
            self._obj = obj
            return self
        if parent:
            obj.ancestor(parent)
        if order:
            obj.order(order)
        for arg in kwargs:
            obj.filter(arg+' =', kwargs[arg])
        self._obj = obj
        self.make_query()
        return self
    
    def make_query(self):
        if self._obj.count() <=1:
            self._obj = self._obj.get()
            self._single_entry = True
        else:
            self._obj.run()
        
    def get_all(self):
        """returns all values + propery names as tuple of dicts"""
        if not self._obj:
            return {}
        properties = self._model.properties()
        res = ()
        obj = self._obj
        if not iterable(self._obj):
            obj = [self._obj]
        for o in obj:
            d = {}
            for p in properties:
                value = getattr(o, p)
                if self._is_Thing and p == 'value':
                    value = pickle.loads(value)
                d[p] = value
            res = res + (d,)
        return res
    
    def set_all(self, dic, parent):
        """ONLY WORKS WITH THINGDB: Sets value of datastore object to dict values corresponding to their key"""
        if self._is_Thing:
            if self._obj:
                for o in self._obj:
                    if o.name in dic:
                        o.value = pickle.dumps(dic.pop(o.name))
                        o.put()
            for d in dic:
                self._model(parent,key_name= d, name = d, value = pickle.dumps(dic[d])).put()
    
    def obj(self):
        return self._obj
    
    def commit(self):
        self._obj.put()
    
    def set_new(self, parent = None, **kw):
        new_obj = self._model(parent = parent, **kw)
        self._obj = new_obj
        return self
        
    def __getattr__(self, name):
        """Returns the value of the attribute""" 
        return getattr(self._obj, name)
    
    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        elif self._obj:
            setattr(self._obj, name, value)
            
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)