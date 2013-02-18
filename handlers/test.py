from handlers.root import Handler
from model.Calendar import Calendar
from model.Group import Group
#from model.Thing import Thing
from model.User import User
from model.Task import Task
#import logging

class Tests(Handler):
    def get(self):
        Group().new('#root', '#admin')
        
        
        
        
        
        
        
        