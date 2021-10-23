import unittest
from ..test import UnitTestBase

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

    def test__login_existing_user__redirects_user_to_home(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__home_route__accessible__when_logged_in(self):
        with self.client as c:
            c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=False)
            response = c.get('/')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__resume_route__accessible__when_not_logged_in(self):
        with self.client as c:
            response = c.get('/about')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.response_has_tag(response, self.RESUME_HTML))
            self.assertTrue(self.user_is_not_authenticated(response))

    def test__resume_route__accessible__when_logged_in(self):
        with self.client as c:
            c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
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
            c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
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
            response = c.get('/reset_password', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.response_has_tag(response, self.REQUEST_PASSWORD_RESET_HTML))
            # redirects to home
            self.assertTrue(self.response_has_tag(response, self.HOME_HTML))
            self.assertTrue(self.user_is_authenticated(response))

    def test__request_password_reset__allowed__for_existing_account(self):
        pass

    def test__request_password_reset__fails_silently__for_nonexistant_account(self):
        pass

    def test__password_reset_email__can_be_used_to_reset_password(self):
        pass

    def test__password_reset_email__can_be_used_to_reset_password__of_account_whose_email_has_been_previously_changed(self):
        pass




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
