from handlers.handler import Handler

from model.User import User
from model.Group import Group
from model.Comments import Comment

import logging

        
        
class Root(Handler):
    def get(self):
        usr = self.verify_user_cookie()
        root = Group('#root')
        comments = Comment().get(root.key, order = "-datetime")
        logging.error(usr)
        self.render('home.html', comments = comments, user = usr)

class Testhtml(Handler):
    def get(self):
        self.render('base.html')