from datetime import datetime
import os
import sys

from flask_blog import create_application, db
from flask_blog.util import load_json

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

def print_if(message, b):
    if b:
        print(message)

def run(verbose):
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
            print_if('Database Rebuilt Successfully', verbose)
        else:
            print('Error Rebuilding Database')

if __name__  == '__main__':
    v = True if '-v' in sys.argv[1:] else False
    run(verbose=v)
