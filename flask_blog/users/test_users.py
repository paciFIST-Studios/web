import io
import os.path
import re
import uuid
import unittest

from flask_blog.test import UnitTestBase
from flask_blog.users.utility import save_profile_image, remove_stored_profile_image

from werkzeug.datastructures import FileStorage
from PIL import Image


class UserModuleTests(UnitTestBase):

    def setUp(self):
        # before each test starts, make sure the current user is logged out
        self.client.get('/logout', follow_redirects=True)

    def tearDown(self):
        pass

    @staticmethod
    def get_registered_user(client, follow_redirects=True):
        username_str = 'user_' + str(uuid.uuid4())[:15]
        user = dict(
            username = username_str
            , email = username_str+'@test.com'
            , password = username_str+'_password'
            , confirm_password = username_str+'_password')
        response = client.post('/register', data=user, follow_redirects=follow_redirects)
        # NOTE: the user dictionary can be passed in as a data parameter, "data=user"
        # in subsequent get calls to the app
        return user, response

    @staticmethod
    def get_user_data_from_account_response(response):
        # data found in the /account page in a get('/account') call
        '''
            <img class="rounded-circle account-img" src="/static/user_profile_images/default.jpg">
                <div class="media-body">
                    <h2 class="account-heading">username</h2>
                    <p class="text-secondary">username@test.com</p>
                </div>
        '''
        lines = response.data.decode('utf-8').split('\n')
        user_account = None
        user_email = None
        user_profile = None
        for line in lines:
            account = re.search('<h2 class=\"account-heading\">(.*)<\/h2>', line)
            if account:
                user_account = account.group(1)

            email = re.search('<p class=\"text-secondary\">(.*)<\/p>', line)
            if email:
                user_email = email.group(1)

            profile = re.search('<img class=\"rounded-circle account-img\" src=\"(.*)\"', line)
            if profile:
                # save just the filename, since we know all images are stored in static/user_profile_images
                user_profile = profile.group(1).split('/')[-1]

        return user_account, user_email, user_profile

    # Tests #############################################################################

    def test__can_register_user__using_register_page(self):
        with self.client as c:
            response = c.post(
                '/register'
                , data=dict(
                    username = 'register_user'
                    , email = 'register_user@test.com'
                    , password = 'register_user_password'
                    , confirm_password = 'register_user_password')
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.LOGIN_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__register_user_page__redirects_to_login_page__after_registration_success(self):
        with self.client as c:
            user, response = self.get_registered_user(c, follow_redirects=False)
            self.assertEqual(response.status, self.CODE_302)
            # bespoke tag for a redirect-to-login page
            self.assertTrue(self.response_has_tag(response, '<a href="/login">/login</a>'))
            # user is not logged in yet
            response = c.get('/')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__can_login__with_registered_user(self):
        with self.client as c:
            # register user
            user, response = self.get_registered_user(c)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.LOGIN_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_not_authenticated(response))
            # login with user
            response = c.post('/login', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))

    def test__can_logout__with_logged_in_user(self):
        with self.client as c:
            # register user
            user, response = self.get_registered_user(c)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.LOGIN_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_not_authenticated(response))
            # login with user
            response = c.post('/login', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))
            # logout with user
            response = c.get('/logout', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__cannot_register_user__using_duplicate_email(self):
        with self.client as c:
            response = c.post(
                '/register'
                , data=dict(username=self.TEST_USER+'asd', email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.REGISTER_HTML))
            # username is valid, email is duplicate
            self.assertTrue(self.response_has_tag(response, self.REGISTRATION_ERROR_EMAIL_INVALID))
            self.assertFalse(self.response_has_tag(response, self.REGISTRATION_ERROR_USERNAME_INVALID))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__cannot_register_user__using_duplicate_username(self):
        with self.client as c:
            response = c.post(
                '/register'
                , data=dict(username=self.TEST_USER, email='asd'+self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.REGISTER_HTML))
            # email is valid, username is duplicate
            self.assertFalse(self.response_has_tag(response, self.REGISTRATION_ERROR_EMAIL_INVALID))
            self.assertTrue(self.response_has_tag(response, self.REGISTRATION_ERROR_USERNAME_INVALID))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__cannot_register_user__with_empty_datafields(self):
        with self.client as c:
            response = c.post(
                '/register'
                , data=dict(username='', email='', password='')
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.REGISTER_HTML))
            # email invalid, username invalid
            self.assertTrue(self.response_has_tag(response, self.REGISTRATION_ERROR_EMAIL_INVALID))
            self.assertTrue(self.response_has_tag(response, self.REGISTRATION_ERROR_USERNAME_INVALID))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__can_visit_account_page__for_existing_test_user(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            response = c.get('/account')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))
            # make sure account page shows the correct information for this user
            username, email, _ = self.get_user_data_from_account_response(response)
            self.assertEqual(self.TEST_USER, username)
            self.assertEqual(self.TEST_EMAIL, email)

    def test__can_visit_account_page__for_registered_user(self):
        with self.client as c:
            user, response = self.get_registered_user(c)
            response = c.post('/login', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            response = c.get('/account', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))
            # make sure account page shows the correct information for this user
            username, email, _ = self.get_user_data_from_account_response(response)
            self.assertEqual(user['username'], username)
            self.assertEqual(user['email'], email)

    def test__can_change_username__for_registered_user(self):
        with self.client as c:
            # get user
            user, response = self.get_registered_user(c)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            # login
            response = c.post('/login', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            # go to account page
            response = c.get('/account', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))
            # show that account page has expected info
            username, email, _ = self.get_user_data_from_account_response(response)
            self.assertEqual(user['username'], username)
            self.assertEqual(user['email'], email)
            # send account update
            user['username'] = 'renamed_user'
            response = c.post('/account', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))
            # verify update success
            new_username, old_email, _ = self.get_user_data_from_account_response(response)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML__UPDATE_SUCCESS))
            self.assertEqual(user['username'], new_username)
            self.assertEqual(user['email'], old_email)

    def test__can_change_email__for_registered_user(self):
        with self.client as c:
            # get user
            user, response = self.get_registered_user(c)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            # login
            response = c.post('/login', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            # go to account page
            response = c.get('/account', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))
            # show that account page has expected info
            username, email, _ = self.get_user_data_from_account_response(response)
            self.assertEqual(user['username'], username)
            self.assertEqual(user['email'], email)
            # send account update
            user['email'] = 'new_email@test.com'
            response = c.post('/account', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))
            # verify update success
            old_username, new_email, _ = self.get_user_data_from_account_response(response)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML__UPDATE_SUCCESS))
            self.assertEqual(user['username'], old_username)
            self.assertEqual(user['email'], new_email)


    def test__unit_test_for__save_profile_image(self):
        with self.app.app_context():
            # ELLIE: I don't think we can use FileStorage with a "with" context manager
            # , as a result, we have to manually close the mock_file to prevent a memory leak
            # , and that's why we're using the try/finally block.
            #   These tests are automated, and we don't want any chance of a leak in something
            #   that'll run a bajillion times without anybody looking into it.
            #   That said, the automated tests should be running in a VM on github, when they do run,
            #   so it "Shouldn't Be A Problem" and "Should Just Work", even if they do leak.
            #   We're manually closing the file anyway

            # mocking the input we'd get from image upload, NOTE: open reads BYTES for stream
            mock_file = FileStorage(stream=open('test.jpg', 'rb'), filename='test.jpg', content_type='jpg')

            path = None
            try:
                # name is the filename, path is the absolute path to the file
                name, path = save_profile_image(mock_file)
                self.assertTrue(name != '')
                self.assertTrue(name in path)
                self.assertFalse(path in name)
                self.assertTrue(os.path.isfile(path))

                if os.path.isfile(path):
                    with Image.open(path) as _image:
                        # the image won't always come out as exactly (125, 125)
                        # , but it should always be smaller than that
                        self.assertTrue(_image.size[0] <= 125)
                        self.assertTrue(_image.size[1] <= 125)
            finally:
                # we need to make sure to delete this file ourselves,
                # b/c we don't want images piling up on the server
                if os.path.isfile(path):
                    os.remove(path)

                # we have to close the mock file to prevent a memory leak
                mock_file.close()

    def test__unit_test_for__remove_stored_profile_image(self):
        with self.app.app_context():
            # not allowed to delete default image
            default_image_path = os.path.join(self.app.root_path, 'static/user_profile_images', 'default.jpg')
            self.assertTrue(os.path.isfile(default_image_path))
            remove_stored_profile_image('default.jpg')
            self.assertTrue(os.path.isfile(default_image_path))

            # ELLIE: I don't think we can use FileStorage with a "with" context manager
            # , as a result, we have to manually close the mock_file to prevent a memory leak
            # , and that's why we're using the try/finally block.
            #   These tests are automated, and we don't want any chance of a leak in something
            #   that'll run a bajillion times without anybody looking into it.
            #   That said, the automated tests should be running in a VM on github, when they do run,
            #   so it "Shouldn't Be A Problem" and "Should Just Work", even if they do leak.
            #   We're manually closing the file anyway

            # mocking the input we'd get from image upload, NOTE: open reads BYTES for stream
            mock_file = FileStorage(stream=open('test.jpg', 'rb'), filename='test.jpg', content_type='jpg')

            path = None
            try:
                name, path = save_profile_image(mock_file)

                self.assertTrue(os.path.isfile(path))
                remove_stored_profile_image(name)
                self.assertFalse(os.path.isfile(path))
            finally:
                # we need to make sure to delete this file ourselves,
                # b/c we don't want images piling up on the server
                if os.path.isfile(path):
                    os.remove(path)

                # we have to close the mock file to prevent a memory leak
                mock_file.close()


    def test__can_change_profile_pic__for_user(self):
        with self.client as c:
            # get user
            user, response = self.get_registered_user(c)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            # login
            response = c.post('/login', data=user, follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            # go to account page
            response = c.get('/account', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))
            # show that account page has expected info
            username, email, _ = self.get_user_data_from_account_response(response)
            self.assertEqual(user['username'], username)
            self.assertEqual(user['email'], email)

            # we have to use a slightly different mock format to supply mocked form data
            # , but we can use a context manager to handle file closing
            with open('test.jpg', 'rb') as infile:
                mock_file = io.BytesIO(infile.read())
                user['image'] = (mock_file, 'test.jpg')

                to_remove = None
                try:
                    # send account update
                    response = c.post('/account', data=user, follow_redirects=True, content_type='multipart/form-data')
                    self.assertEqual(response.status, self.CODE_200)
                    self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
                    self.assertTrue(self.user_is_authenticated(response))

                    _, __, profile = self.get_user_data_from_account_response(response)
                    # verify that the filename changed
                    self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML__UPDATE_SUCCESS))
                    self.assertTrue('.jpg' in profile)
                    self.assertFalse('default.jpg' in profile)

                    profile_image = os.path.join(self.app.root_path, 'static/user_profile_images', profile)
                    default_image = os.path.join(self.app.root_path, 'static/user_profile_images', 'default.jpg')

                    to_remove = profile_image

                    with open(profile_image, 'rb') as p:
                        with open(default_image, 'rb') as d:
                            # assert that these are not the same file, based on file contents
                            self.assertFalse(p.read() == d.read())

                finally:
                    if os.path.isfile(to_remove):
                        os.remove(to_remove)


    # can we reset passwords in the account page?
    # def test__can_change_password__for_existing_user(self):
    #     with self.client as c:
    #         # get user
    #         user, response = self.get_registered_user(c)
    #         self.assertEqual(response.status, self.CODE_200)
    #         self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
    #         # login
    #         response = c.post('/login', data=user, follow_redirects=True)
    #         self.assertEqual(response.status, self.CODE_200)
    #         self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
    #         # go to account page
    #         response = c.get('/account', follow_redirects=True)
    #         self.assertEqual(response.status, self.CODE_200)
    #         self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
    #         self.assertTrue(self.user_is_authenticated(response))
    #         # show that account page has expected info
    #         username, email, profile = self.get_user_data_from_account_response(response)
    #         self.assertEqual(user['username'], username)
    #         self.assertEqual(user['email'], email)
    #         # send account update
    #         user['password'] = 'password'
    #         user['confirm_password'] = 'password'
    #         response = c.post('/account', data=user, follow_redirects=True)
    #         self.assertEqual(response.status, self.CODE_200)
    #         self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
    #         self.assertTrue(self.user_is_authenticated(response))
    #         # check update success
    #         self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML__UPDATE_SUCCESS))
    #         # logout
    #         response = c.get('/logout', follow_redirects=True)
    #         self.assertEqual(response.status, self.CODE_200)
    #         self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
    #         self.assertTrue(self.user_is_not_authenticated(response))
    #         # log back in
    #         response = c.post('/login', data=user, follow_redirects=True)
    #         self.assertEqual(response.status, self.CODE_200)
    #         self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
    #         self.assertTrue(self.user_is_authenticated(response))
    #
    # def test__updated_password_for_existing_user__must_be_valid(self):
    #     pass
