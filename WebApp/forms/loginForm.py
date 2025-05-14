from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField,SubmitField
from wtforms import validators
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    
    name = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), validators.Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    submit = SubmitField("Register")