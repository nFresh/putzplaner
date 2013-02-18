import fix_path
import webapp2

from handlers.user_handler import Login, Signup, Logout, Userroot
from handlers.group_handler import Newgroup, Joingroup, Grouproot, Grouphistory, Groupadmin
from handlers.task_handler import Taskroot, Taskedit
from handlers.admin_handler import Init_app, Admin_Console
from handlers.test import Tests
from handlers.root import Root, Testhtml

GROUP_RE = r"([\w_-](?:[\w_ -]|%20){2,39})"
app = webapp2.WSGIApplication([
    ('/', Root),
    ('/login', Login),
    ('/logout', Logout),
    ('/signup', Signup),
    ('/loggedin', Userroot),
    ('/newgroup', Newgroup),
    ('/joingroup', Joingroup),
    ('/tests', Tests),
    ('/group/' + GROUP_RE, Grouproot),
    ('/group/' + GROUP_RE + '/tasks', Taskroot),
    ('/group/' + GROUP_RE + '/tasks/edit', Taskedit),
    ('/group/' + GROUP_RE + '/history', Grouphistory),
    ('/group/' + GROUP_RE + '/admin', Groupadmin),
    ('/admin/init' , Init_app),
    ('/admin/console' , Admin_Console),
    ('/testhtml' , Testhtml)
], debug=True)