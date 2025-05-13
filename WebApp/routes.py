from flask import render_template, flash, redirect, current_app
from WebApp.extensions import db
from WebApp.models import User

from WebApp.forms.loginForm import LoginForm, RegistrationForm

def register_routes(app):
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
           self.name = name
           self.email = email
            
        def get_email(self):
            return self.email
        
    @app.route("/")
    @app.route("/index")
    def index():
        user = {"username": "John"}
        posts = [
            {
                "author": User("John", "john@uni-pannon.hu"),
                "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            },
            {
                "author": User("Bob", "bob@uni-pannon.hu"),
                "body": "Etiam sit amet lacinia ipsum. Vivamus id commodo arcu."
            },
            {
                "author": User("Kevin", "kevin@uni-pannon.hu"),
                "body": "Maecenas quis commodo nisi, condimentum consectetur."
            }
        ]
        return render_template("index.html", 
                    title="Python Web",
                    user=user, 
                    posts=posts)
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            db_user = db.session.execute(db.select(User).filter_by(
                username=form.username.data)).scalar_one_or_none()
            if db_user:
                flash(f"User {form.username.data} already exists!")
                return redirect("/index")
            else:
                new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
                db.session.add(new_user)
                db.session.commit()
                flash(f"User {form.username.data} registered successfully!")
                return redirect("/index")
        return render_template("register.html", form=form)
        