import datetime

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestAccountMoveLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            [{"name": "My Analytic Plan"}]
        )
        cls.analytic_category_1 = cls.env["account.analytic.category"].create(
            [{"name": "My Analytic Category 1"}]
        )
        cls.analytic_category_2 = cls.env["account.analytic.category"].create(
            [{"name": "My Analytic Category 2"}]
        )
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            [
                {
                    "name": "My Analytic Account 1",
                    "plan_id": cls.analytic_plan.id,
                    "category_id": cls.analytic_category_1.id,
                }
            ]
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            [
                {
                    "name": "My Analytic Account 2",
                    "plan_id": cls.analytic_plan.id,
                    "category_id": cls.analytic_category_2.id,
                }
            ]
        )
        cls.general_account = cls.env["account.account"].create(
            [{"name": "My Income Account", "account_type": "income", "code": "INCOME"}]
        )
        cls.journal = cls.env["account.journal"].create(
            {"code": "J", "name": "Journal", "type": "general"}
        )

    def _get_line_values(self, analytic_account_id):
        values = {
            "account_id": self.general_account.id,
            "analytic_distribution": {str(analytic_account_id): 100},
        }
        if hasattr(self, "move"):
            values["move_id"] = self.move.id
        return values

    def test_analytic_category_ids(self):
        # Create move
        self.move = self.env["account.move"].create(
            {
                "journal_id": self.journal.id,
                "date": datetime.date.today(),
                "line_ids": [
                    Command.create(self._get_line_values(self.analytic_account_1.id))
                ],
            }
        )
        self.assertEqual(
            self.move.line_ids.analytic_category_ids.ids,
            [self.analytic_category_1.id],
        )
        # Update move.
        self.move.write(
            {
                "line_ids": [
                    Command.clear(),
                    Command.create(self._get_line_values(self.analytic_account_2.id)),
                ],
            }
        )
        self.assertEqual(
            self.move.line_ids.analytic_category_ids.ids,
            [self.analytic_category_2.id],
        )
        # Create move line
        self.move_line = self.env["account.move.line"].create(
            self._get_line_values(self.analytic_account_1.id)
        )
        self.assertEqual(
            self.move_line.analytic_category_ids.ids,
            [self.analytic_category_1.id],
        )
        # Update move line
        self.move_line.write(self._get_line_values(self.analytic_account_2.id))
        self.assertEqual(
            self.move_line.analytic_category_ids.ids,
            [self.analytic_category_2.id],
        )
