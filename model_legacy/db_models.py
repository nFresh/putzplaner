from google.appengine.ext import db

class db_Thing(db.Model):
    name = db.StringProperty(required = True)
    value = db.TextProperty(required = True)

class db_User(db.Model):
    name = db.StringProperty(required = True)
    email = db.StringProperty()
    date = db.DateProperty(auto_now_add = True)
    password = db.StringProperty(required = True)

class db_Group(db.Model):
    name = db.StringProperty(required = True)
    owner = db.StringProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    
class db_Task(db.Model):
    name = db.StringProperty(required = True)
    description = db.StringProperty(required = True)
    
class db_Calendar(db.Model):
    datetime = db.DateTimeProperty(required = True)
    task = db.StringProperty(required = True)
    person = db.StringProperty(required = True)
    status = db.StringProperty(required = True)
    
