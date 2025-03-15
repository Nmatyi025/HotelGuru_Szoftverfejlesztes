from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class HotelForm(FlaskForm):
    name = StringField("Hotel Name", validators=[DataRequired(), Length(max=200)])
    location = StringField("Location", validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Create")