import unittest
import onbbits_integration.hooks


class TestHooks(unittest.TestCase):

    def test_hooks_load(self):
        self.assertTrue(onbbits_integration.hooks)