import os.path
import unittest

from . import UnitTestBase

############################################################################################
#
#   These two classes work together to test that the test.db is successfully cleaned up
#   after a test class runs.  Other tests, which determine the integrity of UnitTestBase
#   are located in test/__init__.py
#
############################################################################################
DATABASE_PATH = None
class TestHarnessUnitTests(UnitTestBase):
    def test__test_harness__creates_test_db(self):
        self.assertTrue(os.path.isfile(self.app_db_path))
        global DATABASE_PATH
        DATABASE_PATH = self.app_db_path
class TestHarnessLateUnitTests(unittest.TestCase):
    def test__test_harness__removes_rest_db(self):
        global DATABASE_PATH
        if DATABASE_PATH:
            self.assertFalse(os.path.isfile(DATABASE_PATH))
##############################################################################################

if __name__ == '__main__':
    unittest.main()
