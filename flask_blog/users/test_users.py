import unittest
from ..test import UnitTestBase

class UserModuleTests(UnitTestBase):

    def setUp(self):
        # before each test starts, make sure the current user is logged out
        self.client.get('/logout', follow_redirects=True)

    def tearDown(self):
        pass

    # Tests #############################################################################

    def test__can_create_user__using_register_page(self):
        pass

    def test__can_login__with_created_user(self):
        pass

    def test__can_logout__with_created_user(self):
        pass

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
            c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            response = c.get('/account')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.ACCOUNT_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__can_visit_account_page__for_newly_created_user(self):
        pass

    def test__can_change_username__for_existing_user(self):
        pass

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
