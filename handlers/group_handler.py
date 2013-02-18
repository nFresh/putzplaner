from handlers.handler import Handler
from model.Group import Group
from model.User import User
from model.Task import Task
from model.Comments import Comment
from model.Calendar import Calendar
from lib.utils import valid_groupname

import logging

def group_verify(handler, gname):
    usr = handler.verify_user_cookie()
    grp = Group(gname)
    if usr == "" or not grp.key:
        return (None, None)
    return (grp, usr)

class Newgroup(Handler):
    def get(self):
        usr = self.verify_user_cookie()
        if usr:
            self.formpost(usr)
        else:
            self.redirect("/login")
    
    def formpost(self, usr, grouperror=""):
        self.render('group_new.html', grouperror=grouperror, user = usr)
        
    def post(self):
        usr = self.verify_user_cookie()
        groupname = self.request.get('groupname')
        grouperror = ""
        if usr:
            if Group(groupname).key:
                grouperror = "Name already Taken"
            if not valid_groupname(groupname):
                grouperror = "Invalid Groupname"
            if grouperror != "":
                self.formpost(grouperror)
                return
            Group().new(groupname, usr.name)
            logging.error(usr)
            usr.add_grp(groupname)
            usr.commit()
            self.redirect("/")
            return
        self.redirect("/login")
        
class Joingroup(Handler):
    def get(self):
        jgroup = self.request.get('join')
        usr = self.verify_user_cookie()
        if usr:
            if jgroup !=  "":
                group = Group()
                if group.by_name(jgroup):
                    logging.error(usr.name)
                    group.add_join_request(usr.name)
                    group.commit(True)
                    self.redirect('/')
                    return
            self.formpost(usr)
        else:
            self.redirect("/login")
    
    def formpost(self, usr):
        groups = Group().get_all()
        self.render('group_join.html', groups = groups, user = usr)
            
class Grouproot(Handler):
    def get(self, gname):
        logging.error(gname)
        mod = self.request.get('modstatus')
        grp, usr = group_verify(self, gname)
        if usr and grp:
            if mod != "" and (((grp.members[usr.name])['finish_own_task'] and usr.name == Calendar().get_person(grp.key, mod)) or
                              (grp.members[usr.name])['finish_member_tasks']):
                t = Task(grp.key, mod[:-8])
                intervall = t.intervall
                memberlist = [x for x in grp.members]
                Calendar().make_next(grp.key, mod, memberlist, intervall)
                calendar = Calendar().get(grp.key,True, status = 'Active')
                self.redirect('/group/'+gname)
                return
            tasks = {}
            for task in Task.all(grp.key):
                tasks[task['name']] = task['description']
            calendar = Calendar().get(grp.key, status = 'Active')
            comments = Comment().get(grp.key, order = "-datetime")
            logging.error(calendar)
            self.render('group_root.html', calendar = calendar, user = usr, group = grp,
                         tasks = tasks, comments = comments)
            return
        self.redirect('/')
    
    def post(self, gname):
        grp, usr = group_verify(self, gname)
        comment = self.request.get('comment')
        if usr and grp:
            Comment().set(grp.key, comment, usr.name)
            self.redirect('/group/'+gname)
            

class Grouphistory(Handler):
    def get(self, gname):
        mod = self.request.get('modstatus')
        grp, usr = group_verify(self, gname)
        if usr and grp:
            if mod != "" and ((grp.members[usr.name]['restore_own_task'] and usr == Calendar().get_person(grp.key, mod)) or
                              grp.members[usr.name]['restore_member_tasks']):
                Calendar().reactivate(grp.key, mod)
                self.redirect('/group/'+gname+'/history')
                return
            tasks = {}
            for task in Task.all(grp.key):
                tasks[task['name']] = task['description']
            calendar = Calendar().get(grp.key)
            self.render('group_history.html', calendar = calendar, user = usr, group = grp, tasks = tasks)

class Groupadmin(Handler):
    def get(self, gname):
        grp, usr = group_verify(self, gname)
        acceptusr = self.request.get('acceptuser')
        modusr = self.request.get('moduser')
        if usr and grp:
            members = None
            requests = None
            if usr.name in grp.members:
                rights = grp.members[usr.name]
                if rights['modify_member_rights']:
                    if modusr:
                        modrights = grp.members[modusr]
                        self.render('group_admin_user.html', group = grp, user = usr, modusername = modusr, modrights = modrights)
                        return
                    members = grp.members
                if rights['add_new_members']:
                    if acceptusr:
                        User(acceptusr).add_grp(gname).commit()
                        grp.accept_join_request(acceptusr)
                        grp.commit(True)
                    requests = grp.join_requests
                if members or requests:
                    self.render('group_admin.html', members = members, requests = requests, group = grp, user = usr)
                    return
        self.redirect('/')
    
    def post(self, gname):
        grp, usr = group_verify(self, gname)
        args = self.request.arguments()
        moduser = self.request.get('moduser')
        d = {x : True if self.request.get(x) == 'True' else False for x in args if x != 'moduser'}
        if usr and grp and (usr.name in grp.members) and grp.members[usr.name]['modify_member_rights']:
            grp.members[moduser] = d
            grp.commit(True) #force commit of thing because dict changes can go unnoticed
        self.redirect('/group/'+gname+'/admin')
            
        
                