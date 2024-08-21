# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountAnalyticLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticLine, cls).setUpClass()

        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
            }
        )
        cls.analytic_line = cls.env["account.analytic.line"].create(
            {
                "name": "Test Analytic Line",
                "amount": 100,
                "account_id": cls.analytic_account.id,
            }
        )

    def test_action_edit_analytic_line(self):
        action = self.analytic_line.action_edit_analytic_line()
        self.assertEqual(action["res_id"], self.analytic_line.id)
        self.assertEqual(action["views"], [(False, "form")])

    def test_action_split_analytic_line(self):
        action = self.analytic_line.action_split_analytic_line()
        self.assertEqual(action["context"]["active_id"], self.analytic_line.id)
        self.assertEqual(action["context"]["account_id"], self.analytic_account.id)
        self.assertEqual(action["context"]["amount"], self.analytic_line.amount)
