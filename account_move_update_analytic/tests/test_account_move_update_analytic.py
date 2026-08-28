# Copyright 2026 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.fields import Command
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestAccountAnalyticTagBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        # ==== For Accounting ====
        cls.default_plan = cls.env["account.analytic.plan"].create({"name": "Default"})
        cls.analytic_account_a = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_a",
                "plan_id": cls.default_plan.id,
            }
        )
        cls.analytic_account_b = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_b",
                "plan_id": cls.default_plan.id,
            }
        )
        # ==== For Invoices ====
        cls.tax_id = cls.env["account.tax"].create(
            {
                "name": "Tax 10%",
                "amount_type": "percent",
                "amount": 10.0,
                "analytic": True,
                "type_tax_use": "sale",
            }
        )
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 100.0,
                "taxes_id": [Command.link(cls.tax_id.id)],
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "product_b",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 100.0,
                "taxes_id": [Command.link(cls.tax_id.id)],
            }
        )
        cls.partner_a = cls.env["res.partner"].create(
            {"name": "partner_a", "vat": "999999999"}
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_a.id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "analytic_distribution": {cls.analytic_account_a.id: 100},
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_b.id,
                            "quantity": 2.0,
                            "price_unit": 100.0,
                            "analytic_distribution": {
                                cls.analytic_account_a.id: 100,
                            },
                        },
                    ),
                ],
            }
        )

    def test_update_analytic(self):
        self.invoice.action_post()
        self.assertEqual(
            len(
                self.invoice.line_ids.filtered(
                    lambda line, self=self: line.analytic_distribution
                    == {str(self.analytic_account_a.id): 100}
                )
            ),
            3,
        )
        self.env["account.move.update.analytic.wizard"].create(
            {
                "line_id": self.invoice.invoice_line_ids[0].id,
                "analytic_distribution": {str(self.analytic_account_b.id): 100},
            }
        ).update_analytic_lines()
        # After the update, we should have 2 lines with analytic_account_b
        # and 2 lines with analytic_account_a, because the tax 10% line gets
        # split into two lines, one with analytic_account_a and another one
        # with analytic_account_b
        self.assertEqual(
            len(
                self.invoice.line_ids.filtered(
                    lambda line, self=self: line.analytic_distribution
                    == {str(self.analytic_account_b.id): 100}
                )
            ),
            2,
        )
        self.assertEqual(
            len(
                self.invoice.line_ids.filtered(
                    lambda line, self=self: line.analytic_distribution
                    == {str(self.analytic_account_a.id): 100}
                )
            ),
            2,
        )
