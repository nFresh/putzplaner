from model.Transaction import Transaction

import logging
THINGDB = 'db_Thing'
DEFAULT_THING = {'test': 1}


class Thing(object):
    things_dict = {}
    things_obj = None
    changed = []
    parent = None
    def __init__(self, parent):
        object.__setattr__(self, 'things_dict' , {})
        object.__setattr__(self, 'things_obj', None)
        object.__setattr__(self, 'changed', [])
        object.__setattr__(self, 'parent', None)

        self.things_obj = Transaction(THINGDB, True).query_by_ancestor(parent)
        self.parent = parent
        if self.things_obj:
            things = self.things_obj.get_all()
            for t in things:
                self.things_dict[t['name']] = t['value']
        else:
            self.things_obj = Transaction(THINGDB, True)
            self.things_dict = DEFAULT_THING
            for key in self.things_dict:
                self.changed.append(key)
            
    def get_value(self, key):
        if key not in self.things_dict:
            if key in DEFAULT_THING:
                self.things_dict[key] = DEFAULT_THING[key]
                self.changed.append(key)
            else:
                self.things_dict[key] = None
                return None
        return self.things_dict[key]
    
    def set_value(self, key, value):
        self.things_dict[key] = value
        self.changed.append(key)
    
    def add_value(self, thing_key, dkey, value):
        """adds to a existing dict or creates one, but doesnt create new thing value pair"""
        if thing_key in self.things_dict:
            dic = self.things_dict[thing_key]
            if type(dic) != type({}):
                dic = {}
            dic[dkey] = value
            self.things_dict[thing_key] = dic
            self.changed.append(thing_key)
            return True
        return False
    
    def remove_value(self, thing_key, dkey):
        """removes dict entry from a thing value """
        if thing_key in self.things_dict:
            dic = self.things_dict[thing_key]
            if type(dic) != type({}):
                return
            dic.pop(dkey, None)
    
    def commit(self, force=False):
        """commits all changes to the DB, or forces everything if force == True"""
        if len(self.changed) > 0 or force:           
            self.things_obj.set_all(self.things_dict, self.parent)
            logging.error('commited!!!!!!!!')
        
    def __getattr__(self, name):
        return self.get_value(name)
    
    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            self.set_value(name, value)
            logging.error('SETVALUES!!!!' + name)
    
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)