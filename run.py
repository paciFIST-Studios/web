from flask_blog import create_application

DEBUG=False

app = create_application()

if __name__ == '__main__':
    app.run(debug=DEBUG)
