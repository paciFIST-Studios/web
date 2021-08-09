from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flask_blog import db
from flask_blog.models import Post
from flask_blog.posts.forms import EditPostForm


posts = Blueprint('posts', __name__)


@posts.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    # we use EditPostForm during post creation too
    form = EditPostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'Post created: "{form.title.data}"', 'success')
        return redirect(url_for('main.home'))
    return render_template('edit_post.html', title='Create Post', form=form, legend='Create Post')


@posts.route('/post/<int:post_id>', methods=['GET'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@posts.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Edit Post', form=form, legend='Edit Post')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    title, author = post.title, post.author.username
    db.session.delete(post)
    db.session.commit()
    flash(f'Deleted Post: title={title}, author={author}', 'success')
    return redirect(url_for('main.home'))
