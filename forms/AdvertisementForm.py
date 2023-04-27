from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class AdvertisementForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Скрыть от пользоваетлей")
    photo = FileField('Картинка', validators=[FileAllowed(['jpg', 'png'], 'Только картинки')])
    submit = SubmitField('Применить')
