from google.appengine.ext import db
import logging
class Transaction(object):
    
    def __init__(self, db_model_name):
        self._model = db.class_for_kind(db_model_name)
    
    def query(self, **kwargs):
        """Builds query and returns a tuple of dictionaries -> execute query"""
        parent = kwargs.pop('parent', None)
        key_name = kwargs.pop('key_name', None)
        order = kwargs.pop('order', None)
        limit = kwargs.pop('limit', None)
        query = self._model.all()
        if key_name and parent:
            return self.by_key_name_and_parent(key_name, parent)
        if parent:
            query.ancestor(parent)
        if order:
            query.order(order)
        for arg in kwargs:
            query.filter(arg + ' = ', kwargs[arg])
        return self.execute_query(query, limit)
    
    def execute_query(self, query, limit=None):
        """returns a tuple of dictionaries ({entry.property: entry.value,...},{entry2}...) with every entity in the query"""
        res = ()
        for entity in query.run(limit=limit):
            res = res + (self.unpack_entity(entity),)
        return res
    
    def by_key_name_and_parent(self, key_name, parent):
        entity = self._model.get_by_key_name(key_name, parent)
        return (self.unpack_entity(entity),)
        
    def unpack_entity(self, entity):
        """returns all properties of a db entity and its key as dictionary"""
        if not entity:
            return None
        properties = self._model.properties()
        res = {}
        for p in properties:
            res[p] = getattr(entity, p)
        res['__key__'] = entity.key()
        return res
    
    def set(self, **kwargs):
        entity = self._model(**kwargs)
        entity.put()
        return entity.key()
    
    def update(self, key, values):
        """updates entity with key, values should be a dictionary with property:value pairs"""
        entity = db.get(key)
        for p in values:
            setattr(entity, p, values[p])
        entity.put()
        return True
    
    def delete(self, key):
        entity = db.get(key)
        entity.delete()
        