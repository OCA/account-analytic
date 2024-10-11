import datetime

from odoo.tests.common import TransactionCase


class TestAccountMoveLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            [{"name": "My Analytic Plan"}]
        )
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            [{"name": "My Analytic Account 1", "plan_id": cls.analytic_plan.id}]
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            [{"name": "My Analytic Account 2", "plan_id": cls.analytic_plan.id}]
        )
        cls.general_account = cls.env["account.account"].create(
            [{"name": "My Income Account", "account_type": "income", "code": "INCOME"}]
        )
        cls.journal = cls.env["account.journal"].create(
            {"code": "J", "name": "Journal", "type": "general"}
        )
        cls.move = cls.env["account.move"].create(
            {"journal_id": cls.journal.id, "date": datetime.date.today()}
        )
        cls.move_line = cls.env["account.move.line"].create(
            {
                "move_id": cls.move.id,
                "account_id": cls.general_account.id,
                "analytic_distribution": {str(cls.analytic_account_1.id): 100},
            }
        )

    def test_analytic_account_ids(self):
        self.assertEqual(
            self.move_line.analytic_account_ids.ids,
            [self.analytic_account_1.id],
        )

        self.move_line.analytic_distribution = {str(self.analytic_account_2.id): 100}
        self.assertEqual(
            self.move_line.analytic_account_ids.ids,
            [self.analytic_account_2.id],
        )
