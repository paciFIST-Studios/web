
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return "<H1>Hello World</H1>\nEllie is here"


@app.route('/about')
def about():
    return '<H1>About</H1>'

if __name__ == '__main__':
    app.run(debug=True)
