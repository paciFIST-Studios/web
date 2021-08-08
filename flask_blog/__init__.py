import json
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)

# SECRET KEY ###########################################################################################################
app.config['SECRET_KEY'] = None

SECRET_KEY_FILE_PATH = 'secret_key'
with open(SECRET_KEY_FILE_PATH) as infile:
    app.config['SECRET_KEY'] = infile.read()
    if not app.config['SECRET_KEY']:
        print('WARNING! Could not access secret key')

# DATABASE #############################################################################################################

# the three forward slashes is used to specify a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# classes are called "models".  Each class in the db is it's own table
db = SQLAlchemy(app)

# BCRYPT ###############################################################################################################

# we will use bcrypt for hashing passwords, so we don't have to store any raw passwords
bcrypt = Bcrypt(app)

# LOGIN MANAGER ########################################################################################################

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# EMAIL ################################################################################################################

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None

app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')

if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    with open('email_credentials', 'r') as infile:
        json = json.loads(infile.read())
        app.config['MAIL_USERNAME'] = json['EMAIL_USERNAME']
        app.config['MAIL_PASSWORD'] = json['EMAIL_PASSWORD']

mail = Mail(app)


# Late Import ########################################################################
# we have to import this after the db is set up, in order to prevent circular import
from flask_blog import routes
# Late Import Stop ###################################################################


