# pylint: disable=missing-docstring
import unittest
import pytest_opentmi


class TestVersion(unittest.TestCase):

    def test_version_exists(self):
        """Test that __version__ attribute exists"""
        self.assertIsNotNone(pytest_opentmi.__version__)
        self.assertIsInstance(pytest_opentmi.__version__, str)

    def test_pytest_info_exists(self):
        """Test that __pytest_info__ attribute exists"""
        self.assertIsNotNone(pytest_opentmi.__pytest_info__)
        self.assertTrue(hasattr(pytest_opentmi.__pytest_info__, 'project_name'))
        self.assertTrue(hasattr(pytest_opentmi.__pytest_info__, 'version'))

    def test_pytest_info_values(self):
        """Test that __pytest_info__ has correct values"""
        self.assertEqual(pytest_opentmi.__pytest_info__.project_name, "pytest")
        self.assertIsInstance(pytest_opentmi.__pytest_info__.version, str)
        # pytest version should not be empty
        self.assertTrue(len(pytest_opentmi.__pytest_info__.version) > 0)
