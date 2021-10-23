from ..test import UnitTestBase

from flask_login import current_user, login_manager

#from flask_blog import db, bcrypt
from flask_blog.models import User

class MainModuleTests(UnitTestBase):

    def setUp(self) -> None:
        # before each test starts, make sure the current user is logged out
        self.client.get('/logout', follow_redirects=True)

    def tearDown(self) -> None:
        pass

    def test__main_module__passing_test(self):
        self.assertTrue(True)

    def test__bad_route__returns_404(self):
        response = self.client.get('bad_route')
        self.assertEqual(response.status, self.CODE_404)

    def test__home_route_accessible__when_not_logged_in(self):
        response = self.client.get('/')
        self.assertEqual(response.status, self.CODE_200)
        self.assertTrue(self.MAIN_PAGE_NOT_LOGGED_IN in response.data.decode('utf-8'))

    def test__home_route_accessible__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertTrue(self.MAIN_PAGE_LOGGED_IN in response.data.decode('utf-8'))
            self.assertEqual(response.status, self.CODE_200)
            response = c.get('/account')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.ACCOUNT_EDIT_PAGE in response.data.decode('utf-8'))

    def test__login_is_possible__with_existing_account(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.MAIN_PAGE_LOGGED_IN in response.data.decode('utf-8'))

    def test__login_is_not_possible__with_default_admin_credentials(self):
        # do we even have default admin credentials?
        pass


    def test__resume_route_accessible__when_not_logged_in(self):
        with self.client as c:
            response = c.get('/about')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.RESUME_PAGE in response.data.decode('utf-8'))

    def test__resume_route_accessible__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.MAIN_PAGE_LOGGED_IN in response.data.decode('utf-8'))
            response = c.get('/about')
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.RESUME_PAGE in response.data.decode('utf-8'))

    def test__account_creation_page_accessible__when_not_logged_in(self):
        with self.client as c:
            response = c.get('/register', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.ACCOUNT_CREATION_PAGE in response.data.decode('utf-8'))

    def test__account_creation_page__redirects_to_main__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.MAIN_PAGE_LOGGED_IN in response.data.decode('utf-8'))
            # check that we get a redirect
            response = c.get('/register')
            self.assertEqual(response.status, self.CODE_302)
            self.assertTrue(self.REDIRECT_TO_MAIN_PAGE in response.data.decode('utf-8'))
            # check that the redirect goes to main page
            response = c.get('/register', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.MAIN_PAGE_LOGGED_IN in response.data.decode('utf-8'))

    def test__password_reset_request_accessible__when_not_logged_in(self):
        with self.client as c:
            response = c.get('/reset_password', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertTrue(self.REQUEST_PASSWORD_RESET_PAGE in response.data.decode('utf-8'))

    def test__password_reset_request_not_accessible__when_logged_in(self):
        with self.client as c:
            response = c.post(
                '/login'
                , data=dict(email=self.TEST_EMAIL, password=self.TEST_PASS)
                , follow_redirects=True)
            self.assertTrue(self.MAIN_PAGE_LOGGED_IN in response.data.decode('utf-8'))
            self.assertEqual(response.status, self.CODE_200)
            response = c.get('/reset_password', follow_redirects=True)
            self.assertEqual(response.status, self.CODE_200)
            self.assertFalse(self.REQUEST_PASSWORD_RESET_PAGE in response.data.decode('utf-8'))
            self.assertTrue(self.MAIN_PAGE_LOGGED_IN in response.data.decode('utf-8'))

    def test__password_reset_request_allowed__for_existing_account(self):
        pass

    def test__password_reset_request_fails_silently__for_nonexistant_account(self):
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
