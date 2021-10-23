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
    ERROR_403_HTML = '<!-- testing tag: forbidden 403 -->'
    ERROR_404_HTML = '<!-- testing tag: error 404 -->'
    ERROR_500_HTML = '<!-- testing tag: error 500 -->'
    HOME_HTML = '<!-- testing tag: home page -->'
    LAYOUT_HTML__USER_AUTHENTICATED = '<!-- testing tag: layout user is authenticated -->'
    LAYOUT_HTML__USER_NOT_AUTHENTICATED = '<!-- testing tag: layout user is not authenticated -->'
    LOGIN_HTML = '<!-- testing tag: login page -->'
    PASSWORD_RESET_HTML = '<!-- testing tag: do password reset -->'
    REGISTER_HTML = '<!-- testing tag: register account page -->'
    REGISTRATION_ERROR_EMAIL_INVALID = '<!-- testing tag: email invalid  -->'
    REGISTRATION_ERROR_USERNAME_INVALID = '<!-- testing tag: username invalid  -->'
    # REGISTRATION_ERROR_PASSWORD_INVALID = '<!-- testing tag: password invalid  -->'
    # REGISTRATION_ERROR_CONFIRM_PASSWORD_INVALID = '<!-- testing tag: confirm password invalid  -->'
    REQUEST_PASSWORD_RESET_HTML = '<!-- testing tag: request password reset -->'
    RESUME_HTML = '<!-- testing tag: resume page -->'

    CODE_200 = '200 OK'
    CODE_302 = '302 FOUND'      # redirect
    CODE_404 = '404 NOT FOUND'


    @classmethod
    def setUpClass(cls):
        cls.app = create_application(config_class=USING_CONFIG_CLASS)

        # we'll use the test client to send requests to the application
        cls.client = cls.app.test_client()

        # get db path
        cls.app_root_path = cls.app.config.root_path
        cls.test_db_uri = cls.app.config['SQLALCHEMY_DATABASE_URI']
        cls.test_db_path = os.path.join(cls.app_root_path, cls.test_db_uri.split('///')[-1])

        # it's possible that cleanup of the test db failed on a previous run
        if os.path.isfile(cls.test_db_path):
            os.remove(cls.test_db_path)

        # create test db
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
            db.session.remove()
            db.drop_all()

        # here, we remove the test db.  Note: if the program is interrupted--that's particularly
        # common if you're using breakpoints in an IDE--this code might not run, and therefore
        # we also make a point to remove it just before creation of the test db in setUpClass fn
        if os.path.isfile(cls.test_db_path):
            os.remove(cls.test_db_path)


    @staticmethod
    def response_has_tag(response, tag, decode_as='utf-8'):
        return tag in response.data.decode(decode_as)

    @classmethod
    def user_is_authenticated(cls, response, decode_as='utf-8'):
        return cls.response_has_tag(response, cls.LAYOUT_HTML__USER_AUTHENTICATED, decode_as)

    @classmethod
    def user_is_not_authenticated(cls, response, decode_as='utf-8'):
        return cls.response_has_tag(response, cls.LAYOUT_HTML__USER_NOT_AUTHENTICATED, decode_as)


    @staticmethod
    def get_user_registration_dict(username, email, password):
        return dict(
            username=username
            , email=email
            , password=password
            , confirm_password=password
            # , submit='Sign+Up'
        )


    def test__base_configuration__has_correct_defaults(self):
        # app has been created
        self.assertTrue(self.app)

        # testing client has been exposed to test harness
        self.assertTrue(self.client)

        # testing db should now exist
        self.assertTrue(os.path.isfile(self.test_db_path))

        # we want to run in testing mode, b/c it gives better error messages
        self.assertTrue(self.app.config['TESTING'])

        # we are not testing in debug mode
        self.assertFalse(self.app.config['DEBUG'])

        # our application assumes this is the correct starting point
        self.assertEqual(self.app.config['APPLICATION_ROOT'], '/')

        # security options
        self.assertTrue(self.app.config['SESSION_COOKIE_SECURE'])
        self.assertTrue(self.app.config['REMEMBER_COOKIE_SECURE'])

