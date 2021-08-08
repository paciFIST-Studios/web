import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_blog import app, db, bcrypt, mail
from flask_blog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                              EditPostForm, RequestPasswordResetForm, PasswordResetForm)
from flask_blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from itsdangerous.exc import SignatureExpired

@app.route('/')
def home():
    # request an int, w/ default value=1, from url
    # localhost:port/?page=1
    page = request.args.get(key='page', default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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


@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    # we use EditPostForm during post creation too
    form = EditPostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'Post created: "{form.title.data}"', 'success')
        return redirect(url_for('home'))
    return render_template('edit_post.html', title='Create Post', form=form, legend='Create Post')


@app.route('/post/<int:post_id>', methods=['GET'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        _has_changes = False
        if form.title.data != post.title:
            post.title = form.title.data
            _has_changes = True
        if form.content.data != post.content:
            post.content = form.content.data
            _has_changes = True
        if _has_changes:
            db.session.commit()
            flash(f'Post Updated: id={post.id} title={post.title}', 'success')
        return redirect(url_for('post', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Edit Post', form=form, legend='Edit Post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    title, author = post.title, post.author.username
    db.session.delete(post)
    db.session.commit()
    flash(f'Deleted Post: title={title}, author={author}', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
@login_required
def user_posts(username):
    page = request.args.get(key='page', default=1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Flask Blog: Password Reset Request'
                  , sender='noreply@demo.com'
                  , recipients=[user.email])
    msg.body = f'''{ user.username },
Use this link to reset your password.
{url_for("password_reset", token=token, _external=True)}

If you did not make this request, please contact the web administrator.

If you did make the request, but you don't want to reset your password, you can ignore this email.

Sincerely,
FlaskBlog Team
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'Password Reset Email sent to: "{form.email.data}"', 'info')
        return redirect(url_for('login'))
    return render_template('request_password_reset.html', title='Request Password Reset', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    verify = User.verify_reset_token(token)

    if 'exception' in verify:
        message = verify['exception']
        flash(f'Exception: { message }.', 'warning')
        return redirect(url_for('request_password_reset'))
    else:
        user_id = verify['user_id']
        user = User.query.get(user_id)

    if not user:
        flash(f'Error! Could not locate user in db!', 'warning')
        return redirect(url_for('request_password_reset'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password Reset for "{ user.username }."', 'success')
        return redirect(url_for('login'))

    return render_template('password_reset.html', title='Request Password Reset', form=form)
