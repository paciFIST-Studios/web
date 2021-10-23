import unittest
import os

from flask_blog import create_application, db, bcrypt
from flask_blog.models import User

from ..configuration import TestConfig

USING_CONFIG_CLASS = TestConfig


class UnitTestBase(unittest.TestCase):

    TEST_EMAIL = 'tester@ellielove.com'
    TEST_USER = 'tester'
    TEST_PASS = 'test123'

    ACCOUNT_CREATION_PAGE = '<legend class="border-bottom mb-4">Join Today</legend>'
    ACCOUNT_EDIT_PAGE = '<legend class="border-bottom mb-4">Update Account</legend>'
    MAIN_PAGE_LOGIN_FAILED_STR = '<div class="alert alert-danger">\n                Login Failed!.  Check email and password\n              </div>'
    MAIN_PAGE_NOT_LOGGED_IN = '<a class="nav-item nav-link" href="/login">Login</a>\n              <a class="nav-item nav-link" href="/register">Register</a>'
    MAIN_PAGE_LOGGED_IN = '<a class="nav-item nav-link" href="/account">Account</a>'
    REDIRECT_TO_MAIN_PAGE = '<p>You should be redirected automatically to target URL: <a href="/">/</a>. If not click the link.'
    REQUEST_PASSWORD_RESET_PAGE = '<input class="btn btn-outline-info" id="submit" name="submit" type="submit" value="Request Password Reset">'
    RESUME_PAGE = '<h1>Elizabeth Barrett</h1>\n<p>Software Developer in Test (SDET)\n    <br> Seattle, Washington, USA\n    <br> ellie@paciFIST.studio\n</p>'

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
            # Test user exists in DB for all test suites
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


