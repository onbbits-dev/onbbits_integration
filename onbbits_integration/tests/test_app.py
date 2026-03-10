import frappe
import unittest


class TestOnbbitsIntegration(unittest.TestCase):

    def test_app_installed(self):
        """App should be installed"""
        self.assertIn("onbbits_integration", frappe.get_installed_apps())

    def test_module_exists(self):
        """Module should exist"""
        self.assertTrue(
            frappe.db.exists("Module Def", "Onbbits Integration")
        )

    def test_doctype_exists(self):
        """Settings DocType should exist"""
        self.assertTrue(
            frappe.db.exists("DocType", "OnBBits WA Setting")
        )