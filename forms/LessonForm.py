from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class LessonForm(FlaskForm):
    title = StringField("Название урока", validators=[DataRequired()])
    content = TextAreaField("Название урока", validators=[DataRequired()])
    submit = SubmitField('Применить')
