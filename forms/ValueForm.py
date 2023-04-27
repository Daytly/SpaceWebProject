from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ValueForm(FlaskForm):
    value = IntegerField("Балл")
    submit = SubmitField('Применить')
