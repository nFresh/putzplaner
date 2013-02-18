import random
from model.Task import Task
from model.Group import Group
from handlers.handler import Handler
from lib.utils import validDate, valid_taskname, Datetime_Breakdown
from datetime import datetime, timedelta
from model.Calendar import Calendar

import logging


def task_verify(handler, gname):
    usr = handler.verify_user_cookie()
    taskid = handler.request.get('name')
    if usr and gname:
        return (Group().by_name(gname), usr, taskid)
    return (None, None, None)



class Taskroot(Handler):
    def get(self, gname):
        grp, usr, taskid = task_verify(self, gname)
        if grp and (usr.name in grp.members):
            tasks = Task.all(grp.key)
            self.render('task.html', tasks = tasks, user = usr, group = grp )

class Taskedit(Handler):
    def formpost(self, group, user, taskname="", description = "", intervall = "",
                  ordermethod = "", day = "", month = "", year = "", errors = ""):
        self.render("task_edit.html", group = group, user = user, taskname = taskname, description = description, 
                    intervall = intervall, ordermethod = ordermethod, day = day, month = month, year = year, errors = errors)
    
    def get(self, gname):
        grp, usr, taskid = task_verify(self, gname)
        if grp and (usr.name in grp.members):
            if taskid == '':
                self.formpost(grp, usr)
            else:
                task = Task(grp.key, taskid)
                calendar = Calendar().get(grp.key, task = task.name, status = 'Active')[0]
                day, month, year = Datetime_Breakdown(calendar['datetime'])
                self.formpost(grp,usr, taskid, task.description, task.intervall, task.ordermethod, day, month, year)
        else:
            self.redirect('/')
    
    def post(self, gname):
        grp, usr, taskid = task_verify(self, gname)
        if grp and (usr.name in grp.members):
            taskname = self.request.get('taskname')
            description = self.request.get('description')
            intervall = self.request.get('intervall')
            ordermethod = self.request.get('ordermethod')
            year = self.request.get('year')
            day = self.request.get('day')
            month = self.request.get('month')
            date = validDate(year, month, day)
            first = self.request.get('first')
            error = ""
            if not valid_taskname(taskname):
                error = error + " INVALID Taskname"
            if not intervall.isdigit() and intervall != "":
                error = error + " INVALID intervall"       
            if error != "":
                self.formpost(grp, usr, taskname, description, intervall, ordermethod, day, month, year,  error)
                return
            if not intervall:
                intervall = "7"
            intervall = int(intervall)
            if not date:
                date = datetime.now() + timedelta(days = intervall)
            if first == "random":
                first = random.choice(grp.members.keys())    
            Task().new(grp.key, name = taskname, description = description, intervall = intervall, ordermethod = ordermethod)
            Calendar().delete_active(grp.key, taskname)
            Calendar().set(grp.key, date, taskname, first, 'Active')
            Calendar().get(grp.key,True, status = 'Active')
            self.redirect('/group/'+gname)