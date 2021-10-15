from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import current_user, login_required

from flask_blog import db
from flask_blog.models import StoryFragment
from flask_blog.story_fragments.forms import ViewStoryFragmentsForm, EditStoryFragmentsForm

story = Blueprint('story', __name__)


@story.route('/fragment/<int:fragment_id>', methods=['GET'])
def view(fragment_id):
    fragments = StoryFragment.query.get_or_404(fragment_id)
    return render_template('story_fragments.html', title='Story Fragments', fragments=fragments)

@story.route('/fragment/<int:fragment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_fragment(fragment_id):
    pass


# @story.route('fragment/create', methods=['POST'])
# @login_required
# def create_fragment():
#     fragment_id = 0
#     hashed_id = bcrypt.generate_password_hash(fragment_id).decode('utf-8')
#     pass
