from model.Transaction import Transaction
from datetime import datetime, timedelta
from model.cache import Cache, NoneResult

CALENDARDB = 'db_Calendar'

class Calendar(object):
    
    def get(self, parent, update = False, **kwargs):
        order = kwargs.pop('order', None)
        if not order:
            order = '-datetime'
        res = Cache.get(CALENDARDB, parent,order = order, **kwargs)
        if not res or update:
            res = Transaction(CALENDARDB).query(parent = parent, order = order,  **kwargs)
            Cache.set(CALENDARDB, parent, res if res else NoneResult, **kwargs)
        return None if res == NoneResult else res
    
    def set(self, parent, date, taskname, name, status = "Active"):
        """date can be a int intervall or datetime"""
        key_name = taskname
        if type(date) == type(int()):
            date = datetime.now() + timedelta(days = date)
        if type(date) == type(datetime.now()):
            key_name = key_name + date.strftime('%d%m%Y')
        else:
            return False
        key = Transaction(CALENDARDB).set(parent = parent, key_name = key_name, person = name,
                                          task = taskname, datetime = date, status = status)
        self.get(parent, True)
    
    def delete_active(self, parent, taskname):
        data = Transaction(CALENDARDB).query(parent = parent, task = taskname, status = "Active")
        if len(data) > 0:
            key = (data[0])['__key__']
            Transaction(CALENDARDB).delete(key)
    
    def set_status(self, parent, key_name, status):
        data = (Transaction(CALENDARDB).query(parent = parent, key_name = key_name))[0]
        data['status'] = status
        self.set(parent, data['datetime'], data['task'], data['person'], status)
        return data
    
    def get_person(self, parent, key_name):
        data = (Transaction(CALENDARDB).query(parent = parent, key_name = key_name))[0]
        return data['person']
        
    def reactivate(self, parent, key_name):
        self.delete_active(parent, key_name[:-8])
        self.set_status(parent, key_name, 'Active')
        self.get(parent, True)
        self.get(parent, True, status = 'Active')
        
    def make_next(self, parent, key_name, memberlist, intervall):
        data = self.set_status(parent, key_name, 'Finished')
        name = data['person']
        if name in memberlist:
            i = (memberlist.index(name) + 1) % len(memberlist)
        else:
            i = 0
        self.set(parent, intervall, key_name[:-8], memberlist[i], 'Active')
        self.get(parent, True)
    
        
        