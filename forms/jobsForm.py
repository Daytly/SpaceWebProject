from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    job = StringField("Название работы", validators=[DataRequired()])
    work_size = IntegerField("Продолжительность работ", validators=[DataRequired()])
    collaborators = StringField("id участников через ', '", validators=[DataRequired()])
    start_date = DateField("Дата начала", validators=[DataRequired()])
    is_finished = BooleanField("Статус завершено/не завершено")
    submit = SubmitField('Применить')
