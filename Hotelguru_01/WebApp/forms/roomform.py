from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class RoomForm(FlaskForm):
    room_number = StringField("Room Number", validators=[DataRequired(), Length(max=50)])
    hotel_id = SelectField("Hotel", coerce=int, validators=[DataRequired()])
    capacity = IntegerField("Capacity", validators=[DataRequired(), NumberRange(min=1)])
    price_per_night = FloatField("Price per Night", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Create")