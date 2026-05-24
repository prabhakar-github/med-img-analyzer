from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class LoginForm(FlaskForm):
    """Login form for operator authentication"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=100, message='Username must be between 3 and 100 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Login')
