# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestAnalyticLineCommercialPartner(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_partner = cls.env["res.partner"].create(
            {"name": "Test Company", "is_company": True}
        )
        cls.contact = cls.env["res.partner"].create(
            {"name": "Test Contact", "parent_id": cls.company_partner.id}
        )
        plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test Account", "plan_id": plan.id}
        )
        cls.lines = cls.env["account.analytic.line"].create(
            [
                {
                    "name": "Line contact",
                    "account_id": cls.analytic_account.id,
                    "partner_id": cls.contact.id,
                    "amount": 10,
                },
                {
                    "name": "Line company",
                    "account_id": cls.analytic_account.id,
                    "partner_id": cls.company_partner.id,
                    "amount": 5,
                },
            ]
        )

    def test_commercial_partner(self):
        self.assertEqual(self.lines.commercial_partner_id, self.company_partner)

    def test_search_commercial_partner(self):
        lines = self.env["account.analytic.line"].search(
            [("commercial_partner_id", "=", self.company_partner.id)]
        )
        self.assertEqual(lines, self.lines)

    def test_group_by_commercial_partner(self):
        groups = self.env["account.analytic.line"]._read_group(
            [("id", "in", self.lines.ids)],
            ["commercial_partner_id"],
            ["amount:sum"],
        )
        self.assertEqual(groups, [(self.company_partner, 15)])
