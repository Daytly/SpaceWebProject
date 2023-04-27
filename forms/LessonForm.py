from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, URLField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class LessonForm(FlaskForm):
    title = StringField("Название урока", validators=[DataRequired()])
    content = TextAreaField("Материал", validators=[DataRequired()])
    is_private = BooleanField("Скрыть урок")
    url_videos = URLField('Ссылка на видео материал')
    submit = SubmitField('Применить')
