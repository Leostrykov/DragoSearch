from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired


class SetSettings(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    avatar = FileField('Аватар')
    about = TextAreaField('Обо мне')
    old_password = StringField('Текущий пароль')
    new_password = StringField('Новый пароль')
    repeat_password = StringField('Повторите пароль')
    save = SubmitField('Сохранить')