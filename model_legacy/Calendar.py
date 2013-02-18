from model.Transaction import Transaction
from datetime import datetime, timedelta
from lib.utils import memoize
CALENDARDB = 'db_Calendar'

class Calendar(object):
    
    @memoize('Calendar_by_parent')
    def by_parent(self, parent, **kwargs):
        """Returns a tuple of dicts (see Transaction.get_all()). Use order key argument for sort order"""
        order = kwargs.pop('order', None)
        if not order:
            order = '-datetime'
        obj = Transaction(CALENDARDB).query_by_property_simple(parent = parent, order = order, **kwargs)
        return obj.get_all()
    
    def new(self, parent, date, taskname, name, status = "Active"):
        """ Creates new calendar entry(or overwrites). date can be datetime obj or a int(timedelta in days to today)"""
        key = taskname
        if type(date) == type(int()):
            date = datetime.now() + timedelta(days = date)
        if type(date) == type(datetime.now()):
            key = key + date.strftime('%d%m%Y')
        else:
            return False
        Transaction(CALENDARDB).set_new(parent, key_name = key, datetime = date, task = taskname,
                                               person = name, status = status).commit()
        self.by_parent(parent, status = 'Active', _update = True)
    
    def delete_active(self,parent, taskname):
        """ Deletes the active entry """
        obj = Transaction(CALENDARDB).query_by_property_simple(parent = parent, task = taskname, status = 'Active')
        if obj.obj():
            obj.obj().delete()
    
    def set_status(self, parent, key, status):
        """ Sets the DB entry for parent/key pair to status"""
        obj = Transaction(CALENDARDB).query_by_property_simple(parent = parent, key_name = key)
        obj.status = status
        obj.commit()
        return obj
    
#    @memoize('calendar_get_person')
    def get_person(self, parent, key):
        obj = Transaction(CALENDARDB).query_by_property_simple(parent = parent, key_name = key)
        return obj.person
    
    def Reactivate(self, parent, key):
        self.delete_active(parent, key[:-8] )
        self.set_status(parent, key, 'Active')
        self.by_parent(parent, _update = True)
    
    def Make_next(self, parent, key, memberlist, intervall):
        obj = self.set_status(parent, key, 'Finished')
        name = obj.person
        if name in memberlist:
            i = (memberlist.index(name) + 1) % len(memberlist)
        else:
            i = 0
        self.new(parent, intervall, key[:-8], memberlist[i])
        self.by_parent(parent, status = 'Active', _update = True)
        