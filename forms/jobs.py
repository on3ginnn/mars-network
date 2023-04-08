from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    team_leader = StringField('ID капитана', validators=[DataRequired()])
    job = TextAreaField('Описание работы', validators=[DataRequired()])
    work_size = StringField("Объем работы в часах", validators=[DataRequired()])
    collaborators = StringField("Список id участников")
    is_finished = BooleanField("Завершено")
    submit = SubmitField('Применить')

