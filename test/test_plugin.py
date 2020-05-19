import unittest
from pytest_opentmi.OpenTmiReport import OpenTmiReport


class MockPluginManager:
    def hasplugin(self, plugin):
        return False


class MockConfig:
    pluginmanager = MockPluginManager()

    def getoption(self, opt):
        if opt == 'opentmi':
            return 'https://localhost'
        if opt == 'opentmi_store_logs':
            return False
        raise AssertionError('invalid opt')


class TestPlugin(unittest.TestCase):

    def test_constructor(self):
        report = OpenTmiReport(config=MockConfig())
        self.assertIsInstance(report, OpenTmiReport)

    def test_get_test_key(self):
        report = OpenTmiReport(config=MockConfig())

        class Item:
            @property
            def location(self):
                return ['a', 2, 'b']
        key = report._get_test_key(Item())
        self.assertEqual(key, 'a_2_b')
