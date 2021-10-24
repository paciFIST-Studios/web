from dataclasses import dataclass
import unittest
from ..test import UnitTestBase

@dataclass
class RegisterUser:
    username: str = 'registered_user'
    email: str = 'registered_user@test.com'
    password: str = 'registered_user_123'

class UserModuleTests(UnitTestBase):

    def setUp(self):
        # before each test starts, make sure the current user is logged out
        self.client.get('/logout', follow_redirects=True)

    def tearDown(self):
        pass

    # Tests #############################################################################

    def test__register_user_page__redirects_to_login_page(self):
        with self.client as c:
            response = c.post(
                '/register'
                , data=dict(
                    username='K'+RegisterUser.username
                    , email='K'+RegisterUser.email
                    , password=RegisterUser.password
                    , confirm_password=RegisterUser.password)
                , follow_redirects=False)
            self.assertEqual(response.status, self.CODE_302)
            # bespoke tag for a redirect-to-login page
            self.assertTrue(self.response_has_tag(response, '<a href="/login">/login</a>'))
            # user is not logged in yet
            response = c.get('/')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_not_authenticated(response))


    def test__can_create_user__using_register_page(self):
        with self.client as c:
            response = c.post(
                '/register'
                , data=dict(
                    username=RegisterUser.username
                    , email=RegisterUser.email
                    , password=RegisterUser.password
                    , confirm_password=RegisterUser.password)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.LOGIN_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__can_login__with_created_user(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=RegisterUser.email, password=RegisterUser.password)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))

    def test__can_logout__with_created_user(self):
        with self.client as c:
            c.post(
                '/login'
                , data=dict(email=RegisterUser.email, password=RegisterUser.password)
                , follow_redirects=True)
            response = c.get('/logout', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__cannot_create_user__using_duplicate_email(self):
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

    def test__cannot_create_user__using_duplicate_username(self):
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

    def test__cannot_create_user__with_empty_datafields(self):
        with self.client as c:
            response = c.post(
                '/register'
                , data=dict(username='', email='', password='')
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.REGISTER_HTML))
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

    def test__can_visit_account_page__for_newly_created_user(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=RegisterUser.email, password=RegisterUser.password)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            response = c.get('/account')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__can_change_username__for_existing_user(self):
        pass
        # with self.client as c:
        #     response = c.post(
        #         '/login'
        #         , data=dict(email=RegisterUser.email, password=RegisterUser.password)
        #         , follow_redirects=True)
        #     self.assertEqual(response.status, self.CODE_200)
        #     self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
        #     response = c.post(
        #         '/account'
        #         , data=dict(username='Update'+RegisterUser.username)
        #         , follow_redirects=True)
        #     response = c.get('/account', follow_redirects=True)
        #     self.assertEqual(response.status, self.CODE_200)
        #     self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
        #     self.assertTrue(self.user_is_authenticated(response))

    def test__can_change_profile_pic__for_existing_user(self):
        pass

    def test__can_change_password__for_existing_user(self):
        pass

    def test__updated_password_for_existing_user__must_be_valid(self):
        pass

    #   5. Can change picture of account of created user
    #       a. server removes old picture on update
    #       b. picture is made to small dimension before storage
    #       c. picture gets hashed title before storage

    def test__can_change_email__for_existing_user(self):
        pass



# Test plan for users
#
#   1. Can create user
#   2. Can log in with created user
#   3. Can go to account page of created user
#   4. Can change name of account of created user
#   5. Can change picture of account of created user
#       a. server removes old picture on update
#       b. picture is made to small dimension before storage
#       c. picture gets hashed title before storage
#   6. Can change email of account of created user
#   7. Can log out with created user
#
