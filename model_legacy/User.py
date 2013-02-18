from lib.utils import make_pw_hash, secret_hash
from model.Transaction import Transaction
from model.Thing import Thing
from model.db_models import db_User

USERDB = 'db_User'
USER_THINGS_DEFAULT = {'groups': {},
                       }

class User(object):
    usr = None
    thing = None
    
    def __init__(self, cookie = None):
        object.__setattr__(self, 'usr' , None)
        object.__setattr__(self, 'thing' , None)
        if cookie:
            name = self.validate_cookie(cookie)
            self.by_name(name)
            
    
    def new(self, name, pw, email):      
        password = make_pw_hash(name, pw)
        usr = Transaction(USERDB).set_new(password = password, name = name, email = email)
        self.usr = usr
        usr.commit()
        thing = Thing(usr.obj())
        for t in USER_THINGS_DEFAULT:
            setattr(thing, t, USER_THINGS_DEFAULT[t])
        self.thing = thing
        self.thing.commit()
        return self
        
#   @memoize('USER.__by_name')
    def __by_name(self, name):
        usr = Transaction(USERDB).query_by_property_simple(name = name)
        if usr.obj() == None:
            return (None, None)
        thing = Thing(usr.obj())        
        return (usr, thing)
        
           
    #TODO: CHECK IF USER IS VALID
    def by_name(self, name):
        self.usr, self.thing = self.__by_name(name)
        if self.usr:
            return self
        return None
        
    
    def validate_pw(self, pw):
        pwsalt = self.usr.password.split('|')[1]
        return make_pw_hash(self.usr.name, pw, pwsalt) == self.usr.password
    
    def validate_cookie(self, cookie):
        """Returns username if valid cookie, else None"""
        username, userhash = cookie.split('|')
        return username if secret_hash(username) == userhash else False
        
    def commit(self):
        self.usr.commit()
        self.thing.commit()
    
    def add_group(self, gname):
        return self if self.thing.add_value('groups', gname, '') else None
    
    def __getattr__(self, name):
        if name in db_User.properties():
            return getattr(self.usr, name)
        else:
            res =  getattr(self.thing, name)
            if not res and name in USER_THINGS_DEFAULT:
                return USER_THINGS_DEFAULT[name]
            return res
    
    def __setattr__(self, name, value):    
        if name in self.__dict__:
            self.__dict__[name] = value
        elif name in db_User.properties():
            setattr(self.usr, name, value)
        else:
            setattr(self.thing, name, value)
    
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)