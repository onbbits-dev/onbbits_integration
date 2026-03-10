import frappe
import unittest


class TestOnBBitsWASetting(unittest.TestCase):

    def setUp(self):
        self.doc = frappe.get_doc({
            "doctype": "OnBBits WA Setting",
            "app_name": "Test Application",
            "api_key": "test_key",
            "api_secret": "test_secret"
        })

    def tearDown(self):
        if getattr(self.doc, "name", None) and frappe.db.exists(
            "OnBBits WA Setting", self.doc.name
        ):
            frappe.delete_doc(
                "OnBBits WA Setting",
                self.doc.name,
                force=True
            )

    def test_insert_document(self):
        """Document should insert successfully"""
        self.doc.insert(ignore_permissions=True)
        self.assertTrue(self.doc.name)

    def test_app_name_required(self):
        """app_name should be required"""
        doc = frappe.get_doc({
            "doctype": "OnBBits WA Setting"
        })

        with self.assertRaises(Exception):
            doc.insert(ignore_permissions=True)