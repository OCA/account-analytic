# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import time

from odoo.tests import common


class TestAnalyticDefaultAccount(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.account_analytic_default_model = cls.env["account.analytic.default"]
        cls.analytic_account_model = cls.env["account.analytic.account"]
        cls.move_obj = cls.env["account.move"]
        cls.move_line_obj = cls.env["account.move.line"]

        cls.partner_agrolait = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_4")
        cls.account_receivable = cls.env["account.account"].create(
            {
                "code": "X1035",
                "name": "Income",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.partner_agrolait.property_account_receivable_id = cls.account_receivable.id
        cls.account_sales = cls.env["account.account"].create(
            {
                "code": "X1020",
                "name": "Product Sales - (test)",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
            }
        )

        cls.sales_journal = cls.env["account.journal"].create(
            {
                "name": "Sales Journal - (test)",
                "code": "TSAJ",
                "type": "sale",
                "refund_sequence": True,
                "payment_debit_account_id": cls.account_sales.id,
                "payment_credit_account_id": cls.account_sales.id,
            }
        )

        cls.analytic_account_1 = cls.analytic_account_model.create({"name": "test 1"})
        cls.analytic_account_2 = cls.analytic_account_model.create({"name": "test 2"})
        cls.analytic_account_3 = cls.analytic_account_model.create({"name": "test 3"})
        cls.analytic_account_4 = cls.analytic_account_model.create({"name": "test 4"})

        cls.account_analytic_default_model.create(
            {"product_id": cls.product.id, "analytic_id": cls.analytic_account_1.id}
        )
        cls.account_analytic_default_model.create(
            {
                "partner_id": cls.partner_agrolait.id,
                "analytic_id": cls.analytic_account_2.id,
            }
        )
        cls.account_analytic_default_model.create(
            {
                "product_id": cls.product.id,
                "account_id": cls.account_sales.id,
                "analytic_id": cls.analytic_account_3.id,
            }
        )
        cls.account_analytic_default_model.create(
            {
                "account_id": cls.account_sales.id,
                "analytic_id": cls.analytic_account_4.id,
            }
        )

    def create_move(self, amount=100):
        ml_obj = self.move_line_obj.with_context(check_move_validity=False)
        move_vals = {
            "name": "/",
            "journal_id": self.sales_journal.id,
            "date": time.strftime("%Y") + "-07-25",
        }
        move = self.move_obj.create(move_vals)
        move_line_1 = ml_obj.create(
            {
                "move_id": move.id,
                "name": "/",
                "debit": 0,
                "credit": amount,
                "account_id": self.account_sales.id,
                "product_id": self.product.id,
            }
        )
        move_line_2 = ml_obj.create(
            {
                "move_id": move.id,
                "name": "/",
                "debit": amount,
                "credit": 0,
                "account_id": self.account_receivable.id,
            }
        )
        return move, move_line_1, move_line_2

    def test_account_analytic_default_get_account(self):
        rec = self.account_analytic_default_model.account_get(
            account_id=self.account_sales.id
        )
        self.assertEqual(self.analytic_account_4.id, rec.analytic_id.id)

        rec = self.account_analytic_default_model.account_get(
            account_id=self.account_receivable.id
        )
        self.assertFalse(rec.id)

    def test_account_analytic_default_account_move(self):
        move, move_line_1, move_line_2 = self.create_move()
        self.assertEqual(move_line_1.analytic_account_id, self.analytic_account_4)
        self.assertFalse(move_line_2.analytic_account_id.id)
