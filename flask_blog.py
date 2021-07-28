from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from models import User, Post


# CONFIGURATION ###############################################################

app = Flask(__name__)
app.config['SECRET_KEY'] = None

# the three forward slashes is used to specify a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

with open('secret_key') as infile:
    app.config['SECRET_KEY'] = infile.read()
    if not app.config['SECRET_KEY']:
        print('WARNING! Could not access secret key')

# classes are called "models".  Each class in the db is it's own table
db = SQLAlchemy(app)

###############################################################################



posts = [
    {
        'author': 'Ellie Love',
        'title': 'test post',
        'content': 'first post content',
        'date_posted': '20210724'
    },
    {
        'author': 'Ellie Love 2',
        'title': 'test post 2',
        'content': 'first post content 2',
        'date_posted': '20210724'
    }
]


@app.route('/')
def home():
    return render_template('home.html', posts=posts, title=None)


@app.route('/about')
def about():
    return render_template('about.html', title='Sexy')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for "{ form.username.data }."', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'admin0':
            flash(f'Welcome back { form.email.data }', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful.  Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
