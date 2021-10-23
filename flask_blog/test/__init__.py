import unittest
import os

from flask_blog import create_application, db, bcrypt
from flask_blog.models import User

from ..configuration import TestConfig

USING_CONFIG_CLASS = TestConfig


class UnitTestBase(unittest.TestCase):

    TEST_EMAIL = 'tester@testtest.com'
    TEST_USER = 'tester'
    TEST_PASS = 'test123'

    # these tags exist in the html of different pages, and are used to simplify the
    # testing of different site routes
    ACCOUNT_HTML = '<!-- testing tag: account edit page -->'
    HOME_HTML = '<!-- testing tag: home page -->'
    LAYOUT_HTML__USER_AUTHENTICATED = '<!-- testing tag: layout user is authenticated -->'
    LAYOUT_HTML__USER_NOT_AUTHENTICATED = '<!-- testing tag: layout user is not authenticated -->'
    LOGIN_HTML = '<!-- testing tag: login page -->'
    PASSWORD_RESET_HTML = '<!-- testing tag: do password reset -->'
    REGISTER_HTML = '<!-- testing tag: register account page -->'
    REQUEST_PASSWORD_RESET_HTML = '<!-- testing tag: request password reset -->'
    RESUME_HTML = '<!-- testing tag: resume page -->'

    CODE_200 = '200 OK'
    CODE_302 = '302 FOUND'      # redirect
    CODE_404 = '404 NOT FOUND'


    @classmethod
    def setUpClass(cls):
        cls.app = create_application(config_class=USING_CONFIG_CLASS)

        cls.client = cls.app.test_client()

        # get db path
        cls.app_root_path = cls.app.config.root_path
        cls.app_db_uri = cls.app.config['SQLALCHEMY_DATABASE_URI']
        cls.app_db_path = os.path.join(cls.app_root_path, cls.app_db_uri.split('///')[-1])

        # it's possible that cleanup of the test db failed on a previous run
        if os.path.isfile(cls.app_db_path):
            os.remove(cls.app_db_path)

        with cls.app.app_context():
            db.create_all()
            # Add test user to test db, so different test suites can access db w/o having to register
            hash_word = bcrypt.generate_password_hash(cls.TEST_PASS).decode('utf-8')
            user = User(username=cls.TEST_USER, email=cls.TEST_EMAIL, password=hash_word)
            db.session.add(user)
            db.session.commit()


    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.drop_all()

        if os.path.isfile(cls.app_db_path):
            os.remove(cls.app_db_path)


    @staticmethod
    def response_has_tag(response, tag, decode_as='utf-8'):
        return tag in response.data.decode(decode_as)

    @classmethod
    def user_is_authenticated(cls, response, decode_as='utf-8'):
        return cls.response_has_tag(response, cls.LAYOUT_HTML__USER_AUTHENTICATED, decode_as)

    @classmethod
    def user_is_not_authenticated(cls, response, decode_as='utf-8'):
        return cls.response_has_tag(response, cls.LAYOUT_HTML__USER_NOT_AUTHENTICATED, decode_as)



    def test__base_configuration__has_correct_defaults(self):
        # app has been created
        self.assertTrue(self.app)

        # testing client has been exposed to test harness
        self.assertTrue(self.client)

        # testing db should now exist
        self.assertTrue(os.path.isfile(self.app_db_path))

        # we want to run in testing mode, b/c it gives better error messages
        self.assertTrue(self.app.config['TESTING'])

        # we are not testing in debug mode
        self.assertFalse(self.app.config['DEBUG'])

        # our application assumes this is the correct starting point
        self.assertEqual(self.app.config['APPLICATION_ROOT'], '/')

        # security options
        self.assertTrue(self.app.config['SESSION_COOKIE_SECURE'])
        self.assertTrue(self.app.config['REMEMBER_COOKIE_SECURE'])


