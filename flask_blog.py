
from flask import Flask, render_template, url_for
app = Flask(__name__)

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
def hello_world():
    return render_template('home.html', posts=posts, title=None)


@app.route('/about')
def about():
    return render_template('about.html', title='Sexy')


if __name__ == '__main__':
    app.run(debug=True)
