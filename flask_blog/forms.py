from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_blog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=30)])

    email = StringField('Email', validators=[
        DataRequired(), Email()])

    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6, max=30)])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), Length(min=6, max=30), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        already_taken = User.query.filter_by(username=username.data).first()
        if already_taken:
            raise ValidationError('Username already exists!')

    def validate_email(self, email):
        already_taken = User.query.filter_by(email=email.data).first()
        if already_taken:
            raise ValidationError('Email already exists!')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Email()])

    password = PasswordField('Password', validators=[
    DataRequired(), Length(min=6, max=30)])

    remember_login = BooleanField('Remember Me')

    submit = SubmitField('Login')

