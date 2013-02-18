import webapp2
import jinja2
import os


from model.User import User
from datetime import datetime, timedelta
from lib.utils import secret_hash
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

ADMIN_IP = None

def commentdatetime(d):
    t = datetime.now() - d
    if t.days > 0:
        return str(t.days)+" days"
    if t.seconds > 60:
        if t.seconds > 60*60:
            return str(t.seconds/(60*60)) + " hours"
        return str(t.seconds/(60)) + " minutes"
    return str(t.seconds) + " seconds"
jinja_env.filters['commentdatetime'] = commentdatetime

def newstitle(t):
    return t.split('<endtitle>', 1)[0]
jinja_env.filters['newstitle'] = newstitle

def newsbody(t):
    return t.split('<endtitle>', 1)[1]
jinja_env.filters['newsbody'] = newsbody

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def set_user_cookie(self, name, expires=30):
        """returns complete cookie string"""
        userhash = name + '|' + secret_hash(name)
        dt = datetime.now()
        dt = dt + timedelta(days = 30)
        expires = dt.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        self.response.headers.add_header('Set-Cookie', str('user_id='+userhash+';Path=/; expires="'+expires+'"'))
    
    def verify_user_cookie(self):
        """looks up user_id in cookie and returns name if valid, else None"""
        cookie = self.request.cookies.get('user_id')
        if cookie:
            user, uhash = cookie.split('|')
            return User(user) if secret_hash(user) == uhash else None
        return None
    
    def set_admin_cookie(self, name, expires=30):
        """returns complete cookie string"""
        userhash = name + '|' + secret_hash(name)
        dt = datetime.now()
        dt = dt + timedelta(days = 30)
        expires = dt.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        self.response.headers.add_header('Set-Cookie', str('admin='+userhash+';Path=/; expires="'+expires+'"'))

    def admin_verify(self):
        cookie = self.request.cookies.get('admin')
        ip = self.request.remote_addr
        if cookie and ip == ADMIN_IP:
            user, uhash = cookie.split('|')
            return True if secret_hash(user) == uhash else None
        return None