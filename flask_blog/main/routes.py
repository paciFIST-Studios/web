from flask import Blueprint, render_template, request
from flask_blog.models import Post


main = Blueprint('main', __name__)


@main.route('/')
def home():
    # request an int, w/ default value=1, from url
    # localhost:port/?page=1
    page = request.args.get(key='page', default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, title=None)


@main.route('/about')
def about():
    return render_template('resume.html', title='Resume', hide_side_bar=True)


# STATELESS API SERVICE ########################################################################################
from . import parse_roll_request, roll_dice

@main.route('/dice/<string:data>', methods=['GET'])
def api_request(data):
    roll_request = parse_roll_request(data)
    return roll_dice(roll_request)
