from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# In this case, we're not adding an author field to the post, because these posts will
# come from users on our site.  Therefore, we have to use some kind of relationship between
# a post and a user, to represent authorship.  It is "one to many", because one user can write
# multiple posts (although each post is written by only one user
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # always use utc times
    date_posted = db.Column(db.DateTime , nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Post("{self.title}", "{self.date_posted}")'



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
