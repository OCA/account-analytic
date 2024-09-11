# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestAnalyticLineSplitWizard(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAnalyticLineSplitWizard, cls).setUpClass()

        cls.wizard_obj = cls.env["analytic.line.split.wizard"]
        cls.split_obj = cls.env["analytic.line.split"]
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
        cls.wizard = cls.wizard_obj.with_context(active_id=cls.analytic_line.id).create(
            {
                "amount_total": 100,
            }
        )

    def test_compute_percentage(self):
        line_split = self.split_obj.create(
            {
                "wizard_id": self.wizard.id,
                "account_id": self.analytic_account.id,
                "percentage": 30,
            }
        )
        self.wizard._compute_percentage()
        self.assertEqual(self.wizard.percentage, 70)
        self.assertEqual(line_split.percentage, 30)

    def test_compute_amount(self):
        line_split = self.split_obj.create(
            {
                "wizard_id": self.wizard.id,
                "account_id": self.analytic_account.id,
                "percentage": 30,
            }
        )
        self.wizard._compute_amount()
        self.assertEqual(self.wizard.amount, 70)
        self.assertEqual(line_split.amount, 30)

    def test_action_split_line(self):
        line_split = self.split_obj.create(
            {
                "wizard_id": self.wizard.id,
                "account_id": self.analytic_account.id,
                "percentage": 30,
            }
        )
        self.wizard.action_split_line()
        self.assertEqual(self.analytic_line.amount, 70)
        self.assertEqual(line_split.amount, 30)
        new_line = self.env["account.analytic.line"].search(
            [("parent_line_id", "=", self.analytic_line.id)]
        )
        self.assertIn(new_line, self.analytic_line.child_line_ids)

    def test_check_percentage(self):
        with self.assertRaises(ValidationError):
            self.split_obj.create(
                {
                    "wizard_id": self.wizard.id,
                    "account_id": self.analytic_account.id,
                    "percentage": 110,
                }
            )

    def test_onchange_analytic_line_split_ids(self):
        with self.assertRaises(ValidationError):
            self.split_obj.create(
                {
                    "wizard_id": self.wizard.id,
                    "account_id": self.analytic_account.id,
                    "percentage": 50,
                }
            )
            self.split_obj.create(
                {
                    "wizard_id": self.wizard.id,
                    "account_id": self.analytic_account.id,
                    "percentage": 60,
                }
            )
            self.wizard._onchange_analytic_line_split_ids()
