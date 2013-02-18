from handlers.handler import Handler
from model.User import User
from lib.utils import valid_email, valid_username, valid_password

class Userroot(Handler):
    def get(self):
        usr = self.verify_user_cookie()
        if usr:
            self.render('user_root.html', user = usr)
            return
        self.redirect('/')

class Login(Handler):
    def formpost(self, username="", usrerror="", pwderror=""):
        self.render("login.html", username=username, usrerror=usrerror, pwderror=pwderror, user = None)
    
    def get(self):
        self.formpost()
        
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        usr = User(username)
        if usr.key and usr.validate_pw(password):
            self.set_user_cookie(username)
            self.redirect("/")
            return None
        self.formpost(username, "Wrong Username or Password")
            
class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=;Path=/')
        self.redirect("/login")       
            
            
        

class Signup(Handler):
    def formpost(self, username="", usrerror="",pwderror="", verifyerror="", email="", emailerror=""):
        self.render("signup.html", username=username, usrerror=usrerror, pwderror=pwderror, verifyerror=verifyerror, email=email, emailerror=emailerror, user = None)
        
    def get(self):
        self.formpost()
        
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        usrerror = pwderror = verifyerror = emailerror = ""
        usr = User()
        if not valid_username(username):
            usrerror = "Invalid Username!"
        if not valid_password(password):
            pwderror = "invalid Password!"
        if not valid_email(email) and email != '':
            emailerror = 'Invalid Email!'
        if password != verify:
            verifyerror = "Passwords don't match!"
        if usr.by_name(username):
            usrerror= "Username already in use!"
        if usrerror or pwderror or verifyerror or emailerror:
            self.formpost(username, usrerror, pwderror, verifyerror, email, emailerror)
            return None
        else:
            usr.new(username, password, email)
            self.set_user_cookie(username)
            self.redirect("/")
