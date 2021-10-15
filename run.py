from flask_blog import create_application

DEBUG=False

if __name__ == '__main__':
    # how do I push to production?
    # https://gist.github.com/lemiorhan/8912188

    app = create_application()
    app.run(debug=DEBUG)
