from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = None

# the three forward slashes is used to specify a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

SECRET_KEY_FILE_PATH = 'secret_key'
with open(SECRET_KEY_FILE_PATH) as infile:
    app.config['SECRET_KEY'] = infile.read()
    if not app.config['SECRET_KEY']:
        print('WARNING! Could not access secret key')

# classes are called "models".  Each class in the db is it's own table
db = SQLAlchemy(app)

# we will use bcrypt for hashing passwords, so we don't have to store any raw passwords
bcrypt = Bcrypt(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Late Import ########################################################################
# we have to import this after the db is set up, in order to prevent circular import
from flask_blog import routes
# Late Import Stop ###################################################################


