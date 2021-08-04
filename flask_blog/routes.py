import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flask_blog import app, db, bcrypt
from flask_blog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

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
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for "{ form.username.data }."', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_login.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Failed!.  Check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_profile_image(image):
    # make a random file name (but not a random file extension) in order to prevent
    # profile picture file path collisions
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(image.filename)
    image_file_name = random_hex + ext
    image_storage_path = os.path.join(app.root_path, 'static/user_profile_images', image_file_name)

    # resize image to 125x125
    storage_size = (125, 125)
    _image = Image.open(image)
    _image.thumbnail(storage_size)

    # save from the resized file
    _image.save(image_storage_path)
    return image_file_name

def remove_stored_profile_image(filename):
    # note: don't delete our default image.
    # happens the first time user attempts to update their profile
    if filename == 'default.jpg':
        return
    _image = os.path.join(app.root_path, 'static/user_profile_images', filename)
    if os.path.isfile(_image):
        os.remove(_image)

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        _has_changes = False

        # username
        if current_user.username != form.username.data:
            current_user.username = form.username.data
            _has_changes = True

        # email
        if current_user.email != form.email.data:
            current_user.email = form.email.data
            _has_changes = True

        # profile image
        if form.image.data:
            image_file = save_profile_image(form.image.data)
            to_remove = current_user.image_file
            current_user.image_file = image_file
            remove_stored_profile_image(filename=to_remove)
            _has_changes = True

        # commit changes to db
        if _has_changes:
            db.session.commit()
            flash('Your account has been updated', 'success')
        else:
            flash('No updates to account', 'info')

        # perform redirect, according to POST-GET-REDIRECT pattern
        return redirect(url_for('account'))

    # pre-populate form with existing data
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename=f'user_profile_images/{current_user.image_file}')
    return render_template('account.html', title='Account', image_file=image_file, form=form)
