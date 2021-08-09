from flask_blog import create_application

DEBUG=True

if __name__ == '__main__':
    app = create_application()
    app.run(debug=DEBUG)
