from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, URLField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    title = StringField("Название теста", validators=[DataRequired()])
    url = URLField("Ссылка на yandexForm", validators=[DataRequired()])
    submit = SubmitField('Применить')
