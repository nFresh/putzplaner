from handler import Handler
from model.User import User
from model.Group import Group
from lib.utils import make_pw_hash
from model.Comments import Comment
import logging

INIT_PW = 'asshat'




class Init_app(Handler):
    def get(self):
        usr = self.verify_user_cookie()
        adminusr = User('#admin')
        if adminusr.key:
            self.response.out.write('NICE TRY WISE GUY!')
            return
        elif usr:
            self.render('admin_init.html', user  = usr)
        else:
            self.response.out.write('Please create a User First and log in!')

    def post(self):
        usr = self.verify_user_cookie()
        pw = self.request.get('password')
        new_pw = self.request.get('new_password')
        new_pw_confirm = self.request.get('new_pw_confirm')
        if pw == INIT_PW and new_pw == new_pw_confirm and usr:
            admin = User().new('#admin', make_pw_hash('#admin', new_pw),'')
            Group().new('#root', 'admin')
            usr.isAdmin = True
            usr.commit()
            admin.isAdmin = True
            admin.commit()
            ADMIN_IP = self.request.remote_addr
            self.set_admin_cookie('#admin')
            self.redirect('/admin/console')
            
            return
        self.redirect('/')

class Admin_Console(Handler):
    def get(self):
        usr = self.verify_user_cookie()
        if usr and usr.isAdmin:
            self.render('admin_console.html', user = usr)
    
    def post(self):
        usr = self.verify_user_cookie()
        if usr and usr.isAdmin:
            news = self.request.get('news')
            title = self.request.get('title')
            if news and title:
                grp = Group('#root')
                text = title + ' <endtitle> ' + news
                Comment().set(grp.key, text , usr.name)
                self.redirect('/admin/console')
            