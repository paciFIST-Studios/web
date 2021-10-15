from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_paranoid import Paranoid

from flask_blog.configuration import Config


db = SQLAlchemy()

# we will use bcrypt for hashing passwords, so we don't have to store any raw passwords
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
# note: session protections are handled by Paranoid
login_manager.session_protection = None

mail = Mail()

def create_application(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # https://github.com/miguelgrinberg/flask-paranoid
    paranoid = Paranoid(app)
    paranoid.redirect_view = '/'

    from flask_blog.users.routes import users
    from flask_blog.posts.routes import posts
    from flask_blog.main.routes import main
    from flask_blog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    # minor changes: push to server testing
    # test I hope I didn't break main

    return app

