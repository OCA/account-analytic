# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import SavepointCase


class TestStockAnalyticNever(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_obj = cls.env["account.account"]
        cls.move_obj = cls.env["account.move"].with_context(check_move_validity=False)
        cls.move_line_obj = cls.env["account.move.line"].with_context(
            check_move_validity=False
        )
        cls.analytic_account_obj = cls.env["account.analytic.account"]
        cls.analytic_account = cls.analytic_account_obj.create({"name": "test aa"})
        cls.sales_journal = cls.env["account.journal"].create(
            {
                "name": "Sales Journal - (test)",
                "code": "TSAJ",
                "type": "sale",
            }
        )
        cls.analytic_account_1 = cls.analytic_account_obj.create(
            {"name": "test aa 1 for distribution"}
        )
        cls.analytic_account_2 = cls.analytic_account_obj.create(
            {"name": "test aa 2 for distribution"}
        )
        cls.analytic_tag_obj = cls.env["account.analytic.tag"]
        cls.analytic_distribution_obj = cls.env["account.analytic.distribution"]
        cls.account_sales = cls.account_obj.create(
            {
                "code": "X1020",
                "name": "Product Sales - (test)",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
            }
        )
        cls.account_sales.user_type_id.property_analytic_policy = "never"

        cls.account_recv = cls.account_obj.create(
            {
                "code": "X11002",
                "name": "Debtors - (test)",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
            }
        )

    def test_account_analytic_never(self):
        date = fields.Datetime.now()
        move_vals = {"name": "/", "journal_id": self.sales_journal.id, "date": date}
        move = self.move_obj.create(move_vals)
        move_line = self.move_line_obj.create(
            {
                "move_id": move.id,
                "name": "/",
                "debit": 0,
                "credit": 15.0,
                "account_id": self.account_sales.id,
                "analytic_account_id": self.analytic_account.id,
            }
        )
        self.move_line_obj.create(
            {
                "move_id": move.id,
                "name": "/",
                "debit": 15.0,
                "credit": 0,
                "account_id": self.account_recv.id,
            }
        )

        self.assertFalse(
            move_line.analytic_account_id,
        )
