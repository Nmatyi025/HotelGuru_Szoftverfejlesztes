from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class SearchForm(FlaskForm):
    search_text = StringField("Search", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Search")
