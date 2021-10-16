from datetime import datetime
import os
import sys

from flask_blog import create_application, bcrypt, db
from flask_blog.util import load_json

from flask_blog.models import Post, User

def get_testing_data():
    return {
        'username':'test1',
        'email':'test1@test.com',
        'password':'test1password',
        'post1':{
                'title':'Test Blog Post',
                'content':'This post was generated during a database rebuild'
        },
        'post2':{
                'title':'Additional Testing Post',
                'content':'Remember: Testing user { "username":"test1", '
                          ' "email":"test1@test.com", "password":"test1password"}'
        }
    }

def get_configuration():
    secret = '/etc/web.config.json'
    config = load_json(secret)
    return config

def existing_database_detected(config):
    file_name = config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]
    file_path = os.path.join(os.getcwd(), 'flask_blog', file_name)
    if os.path.isfile(file_path):
        return True
    return False

def rename_existing_database(config):
    # old name
    file_name = config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]
    path_to_file = os.path.join(os.getcwd(), 'flask_blog')
    file_path = os.path.join(path_to_file, file_name)
    # new name
    new_name = datetime.now().strftime('%Y%m%d_%H%M%S_') + file_name
    new_file_path = os.path.join(path_to_file, new_name)
    # rename
    if os.path.isfile(file_path):
        os.rename(file_path, new_file_path)
        return new_file_path
    return None

def add_test_data_to_db(db, app):
    app.app_context().push()
    data = get_testing_data()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(user)
    # commit the user, b/c that gives the user an id, and we need the idea to make the post
    db.session.commit()

    post1 = Post(title=data['post1']['title'], content=data['post1']['content'], user_id=user.id)
    post2 = Post(title=data['post2']['title'], content=data['post2']['content'], user_id=user.id)
    db.session.add(post1)
    db.session.add(post2)
    db.session.commit()

def print_if(message, b):
    if b:
        print(message)

def run(verbose, test_data):
    print_if('Now Rebuilding Database', verbose)
    print_if('Searching for system configuration', verbose)
    config = get_configuration()
    if not config:
        print_if('System Configuration Not Found!', verbose)
        print_if('Exiting', verbose)
        print_if('See Flask-SQLAlchemy::Contexts docs for more information: '+
              'https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/', verbose)
        return False
    else:
        print_if('System Configuration Found', verbose)

    start_rebuild = True
    print_if('Checking For Existing Database', verbose)
    if existing_database_detected(config):
        print_if('Existing Database Found', verbose)
        print_if('Moving Existing Database', verbose)
        path = rename_existing_database(config)
        if path:
            print('Previous Database Moved To: '+path)
        else:
            print('ERROR: Database Not Found')
            start_rebuild = False
    else:
        print_if('Existing Database Not Found', verbose)

    if not start_rebuild:
        print('Cannot guarantee safety of any existing database.  Continue?')
        if input('Y/n?').lower() == 'y':
            start_rebuild = True

    if start_rebuild:
        print_if('Starting Database Rebuild', verbose)
        app = create_application()
        print_if('Creating Database Tables', verbose)
        db.create_all(app=app)
        if existing_database_detected(config):
            if test_data:
                print_if('Database Recreated. Adding Test Information', verbose)
                add_test_data_to_db(db, app)
                data = get_testing_data()
                print_if('Testing Data:'+str(data), verbose)
                print_if('\nTest Account:\n    email: {}\n    password: {}'.format(
                    data['email'], data['password']), verbose)
        else:
            print('Error Rebuilding Database')
    print_if('Database Rebuilt Successfully', verbose)

if __name__  == '__main__':
    v = True if '-v' in sys.argv[1:] else False
    t = True if '-t' in sys.argv[1:] else False
    h = True if '-h' in sys.argv[1:] else False
    if not h:
        run(verbose=v, test_data=t)
    else:
        print('''
    python3 create_new_database.py -v   creates db, verbose commentary
    python3 create_new_database.py -t   creates db, test data
    python3 create_new_database.py -h   shows help

    python3 create_new_database.py -v -t   creates db, test data, verbose
        ''')
