# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestResPartner(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.organization = cls.env["account.analytic.organization"].create(
            {"name": "North"}
        )
        cls.company = cls.env["res.partner"].create(
            {"name": "ACME", "is_company": True}
        )
        cls.contact = cls.env["res.partner"].create(
            {"name": "Bob", "parent_id": cls.company.id}
        )
        cls.delivery_address = cls.env["res.partner"].create(
            {"type": "delivery", "parent_id": cls.company.id}
        )

    def test_display_name(self):
        self.assertEqual(self.contact.display_name, "ACME, Bob")
        self.assertEqual(self.delivery_address.display_name, "ACME, Delivery Address")
        self.contact.analytic_org_id = self.organization
        self.assertEqual(self.contact.display_name, "ACME, Bob (North)")
