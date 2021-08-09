from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
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


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=30)])

    email = StringField('Email', validators=[
        DataRequired(), Email()])

    image = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png'])
    ])

    submit = SubmitField('Update')

    def validate_username(self, username):
        # if no change, skip validation
        if username.data == current_user.username: return

        already_taken = User.query.filter_by(username=username.data).first()
        if already_taken:
            raise ValidationError('Username already exists!')

    def validate_email(self, email):
        # if no change, skip validation
        if email.data == current_user.email: return

        already_taken = User.query.filter_by(email=email.data).first()
        if already_taken:
            raise ValidationError('Email already exists!')


class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Email()])

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user_email = User.query.filter_by(email=email.data).first()
        if user_email is None:
            raise ValidationError(f'No Account Registered for: "{email.data}"')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6, max=30)])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), Length(min=6, max=30), EqualTo('password')])

    submit = SubmitField('Update Password')
