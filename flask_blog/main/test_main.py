import json
from random import randint

import unittest
from ..test import UnitTestBase

from . import HELP_MESSAGE

class MainModuleTests(UnitTestBase):

    def setUp(self):
        # before each test starts, make sure the current user is logged out
        self.client.get('/logout', follow_redirects=True)

    def tearDown(self):
        pass

    # Tests #############################################################################

    def test__bad_route__returns_404__when_logged_out(self):
        response = self.client.get('bad_route')
        self.assertEqual(response.status, self.CODE_404)
        self.assertTrue(self.response_has_tag(response, self.ERROR_404_HTML))
        self.assertTrue(self.user_is_not_authenticated(response))

    def test__bad_route__returns_404__when_logged_in(self):
        with self.client as c:
            c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            response = self.client.get('bad_route')
            self.assertEqual(response.status, self.CODE_404)
            self.assertTrue(self.response_has_tag(response, self.ERROR_404_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__home_route__accessible__when_not_logged_in(self):
        with self.client as c:
            response = c.get('/')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__cannot_login__without_credentials(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email='', password='')
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            # no redirect
            self.assertTrue(self.response_has_tag(response, self.LOGIN_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__cannot_login__with_invalid_credentials(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email='thisisnotaregistereduser@test.com', password='five')
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            # no redirect
            self.assertTrue(self.response_has_tag(response, self.LOGIN_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__user_can_login__with_valid_credentials(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))

    def test__user_can_logout__after_login_with_valid_credentials(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))
            response = c.get('logout', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__login_existing_user__redirects_user_to_home(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))

    def test__home_route__accessible__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=False)
            self.assertEqual(response.status, self.CODE_302)
            response = c.get('/')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))

    def test__resume_route__accessible__when_not_logged_in(self):
        with self.client as c:
            response = c.get('/about')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.RESUME_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__resume_route__accessible__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))
            response = c.get('/about')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.RESUME_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__register_account_page__accessible__when_not_logged_in(self):
        with self.client as c:
            response = c.get('/register', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.REGISTER_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__register_account_page__redirects_to_home__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))
            response = c.get('/register', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__request_password_reset__accessible__when_logged_out(self):
        with self.client as c:
            response = c.get('/reset_password', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.REQUEST_PASSWORD_RESET_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__request_password_reset__not_accessible__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertFalse(self.response_has_tag(response, self.LOGIN_FAIL_MESSAGE))
            self.assertTrue(self.user_is_authenticated(response))
            response = c.get('/reset_password', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.REQUEST_PASSWORD_RESET_HTML))
            # redirects to home
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__request_password_reset__allowed__for_existing_account(self):
        pass

    def test__request_password_reset__fails_silently__for_nonexistent_account(self):
        # with self.client as c:
        #     response = c.get('/reset_password', follow_redirects=True)
        #     self.assertEqual(response.status, self.CODE_200)
        #     self.assertFalse(self.response_has_tag(response, self.REQUEST_PASSWORD_RESET_HTML))
        #     # redirects to home
        #     self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
        #     self.assertTrue(self.user_is_authenticated(response))
        pass

    def test__password_reset_email__can_be_used_to_reset_password(self):
        pass

    def test__password_reset_email__can_be_used_to_reset_password__of_account_whose_email_has_been_previously_changed(self):
        pass


    def test__dice_api__returns_correct_values__for_correct_request(self):
        with self.client as c:
            for i in range(10):
                count = randint(1, 10)
                size = randint(1, 20)
                modifier = randint(0, 10)
                command = f'{count}d{size}+{modifier}'
                response = c.get(f'/dice/{command}')
                self.assertEqual(response.status, self.CODE_200)
                self.assertEqual(response.content_type, 'application/json')
                data = json.loads(response.data.decode('utf-8'))
                self.assertEqual(data['request'], command)
                self.assertEqual(len(data['rolls']), count)
                self.assertTrue(int(data['total']) <= count * size + modifier)

    def test__dice_api__returns_help_message__for_malformed_request(self):
        with self.client as c:
            response = c.get(f'/dice/45')
            self.assertEqual(response.status, self.CODE_200)
            # note: the help message is not json
            self.assertEqual(response.content_type, 'text/html; charset=utf-8')
            data = response.data.decode('utf-8')
            self.assertEqual(data, HELP_MESSAGE)

if __name__ == '__main__':
    unittest.main()

#
#   Test plan for main
#
#   1. Can view home route without being logged in
#   2. Can view home route while logged in
#   3. Can view post feed while not logged in
#   4. Can view post feed while logged in
#   5. Can view resume page while not logged in
#   6. Can view resume page while logged in
#   7. Can get to account creation page while not logged in
#   8. Cannot get to account creation page while logged in
#   9. Can request password reset for existing user account
#  10. Can request password reset for non-existing user account (but it does nothing)
#  11. Can use email to reset password for existing user account
#  12. Can use email to reset password for existing user account, whose email has been updated to new address
#
#
