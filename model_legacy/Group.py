
from model.Transaction import Transaction
from model.Thing import Thing
from db_models import db_Group
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
    grp = None
    thing = None
    
    def __init__(self):
        object.__setattr__(self, 'grp', None)
        object.__setattr__(self, 'thing', None)
    
    def new(self, name, owner):
        grp = Transaction(GROUPDB).set_new(name=name, owner=owner)
        grp.commit()
        thing = Thing(grp.obj())
        for t in GROUP_THINGS_DEFAULT:
            setattr(thing, t, GROUP_THINGS_DEFAULT[t])
        thing.members[owner] = GROUP_PERMISSIONS_OWNER
        thing.commit()
        self.grp = grp
        self.thing = thing
       
        
    def __by_name(self, name):
        grp = Transaction(GROUPDB).query_by_property_simple(name = name)
        if not grp.obj():
            return (None, None)
        thing = Thing(grp.obj())
        return (grp, thing)
    
    def by_name(self, name):
        self.grp, self.thing = self.__by_name(name)
        if self.grp:
            return self
        return None
    
    def obj(self):
        return self.grp.obj()
    
    @classmethod
    def get_all(cls):
        """Gets all Group entries and returns them as a list of dics"""
        grps = Transaction(GROUPDB).query_by_property_simple().get_all()
        return grps
    
    def commit(self, force=False):
        """ If force = True, thing will be commited even without changes"""
        self.grp.commit()
        self.thing.commit(force)
    
    def add_join_request(self, name, msg = ""):
        return self.thing.add_value('join_requests', name,  msg)
    
    def remove_join_request(self, name):
        return self.thing.remove_value('join_requests', name)
    
    def add_member(self, name, permissions = GROUP_PERMISSIONS_DEFAULT):
        self.thing.add_value('members', name, permissions)
    
    def accept_join_request(self, name, permissions = GROUP_PERMISSIONS_DEFAULT):
        self.remove_join_request(name)
        self.add_member(name, permissions)
               
    def __getattr__(self, name):
        if name in db_Group.properties():
            return getattr(self.grp, name)
        else:
            return getattr(self.thing, name)
    
    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        elif name in db_Group.properties():
            setattr(self.grp, name, value)
        else:
            setattr(self.thing, name, value)