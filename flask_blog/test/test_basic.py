import os
import unittest

from flask_blog import create_application, db, mail

from ..configuration import TestConfig

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = create_application(config_class=TestConfig)
        self.assertEqual(self.app.debug, False)

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test__passing_test(self):
        self.assertTrue(True)

    def test__home_page_test(self):
        #response = self.app.get('/', follow_redirects=True)
        #self.assertEqual(response.status_code, 200)
        pass


if __name__ == '__main__':
    unittest.main()
