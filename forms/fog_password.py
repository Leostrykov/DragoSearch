from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class FogPassword(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    submit = SubmitField('Войти')
