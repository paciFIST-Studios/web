import os

from flask_blog.util import load_json

secret = '/etc/web.config.json'
config = load_json(secret)

class Config:
    SECRET_KEY = config.get("SECRET_KEY") if config else os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = config.get("SQLALCHEMY_DATABASE_URI") \
        if config else os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = config.get("EMAIL_USERNAME") if config else os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = config.get("EMAIL_PASSWORD") if config else os.environ.get('EMAIL_PASSWORD')

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

class TestConfig:
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = config.get('EMAIL_USERNAME') if config else os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = config.get('EMAIL_PASSWORD') if config else os.environ.get('EMAIL_PASSWORD')

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = False
