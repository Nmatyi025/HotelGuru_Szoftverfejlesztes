from WebApp import app, db
from flask import render_template, flash, redirect
from WebApp.models import User


from WebApp.forms.loginForm import LoginForm
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_user = db.session.execute(db.select(User).filter_by(
            username=form.username.data)).scalar_one()
        if db_user.check_password(form.password.data):
            flash(f"Login requested for user {form.username.data}")
            global user
            user = db_user
            return redirect("/index")
        else:
            flash(f"Wrong username or password!")
            return redirect("/index")
    return render_template("login.html", user=User, form=form)

class User:
    def __init__(self, name, email):
        self.name =name
        self.email = email
        
    def get_email(self):
        return self.email
    
@app.route("/")
@app.route("/index")
def index():
    user = {"username" :  "John" }
    posts = [
                {
                    "author" : User("John", "john@uni-pannon.hu"),
                    "body" : "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
                },
                {
                    "author" : User("Bob", "bob@uni-pannon.hu"),
                    "body" : "Etiam sit amet lacinia ipsum. Vivamus id commodo arcu."
                },
                {
                    "author" : User("Kevin", "kevin@uni-pannon.hu"),
                    "body" : "Maecenas quis commodo nisi, condimentum consectetur."
                }
                
            ]
    return render_template("index.html", 
                   title = "Python Web",
                   user = user, 
                   posts = posts
                          )