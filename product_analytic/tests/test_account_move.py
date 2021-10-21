# Copyright 2015 Antiun Ingenieria - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestAccountInvoiceLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.analytic_account1 = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account1"}
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account2"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
                "lst_price": 50,
                "standard_price": 50,
                "income_analytic_account_id": cls.analytic_account1.id,
                "expense_analytic_account_id": cls.analytic_account2.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test journal sale", "code": "SALE0", "type": "sale"}
        )
        cls.journal_purchase = cls.env["account.journal"].create(
            {"name": "Test journal purchase", "code": "PURCHASE0", "type": "purchase"}
        )
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test account type", "type": "other", "internal_group": "equity"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
            }
        )

    def test_create_in(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.journal_purchase.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "quantity": 1,
                            "price_unit": 50,
                            "account_id": self.account.id,
                            "product_id": self.product.id,
                        },
                    )
                ],
            }
        )
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line._onchange_product_id()
        self.assertEqual(
            invoice_line.analytic_account_id.id,
            self.product.expense_analytic_account_id.id,
        )

    def test_create_out(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.journal_sale.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "quantity": 1,
                            "price_unit": 50,
                            "account_id": self.account.id,
                            "product_id": self.product.id,
                        },
                    )
                ],
            }
        )
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line._onchange_product_id()
        self.assertEqual(
            invoice_line.analytic_account_id.id,
            self.product.income_analytic_account_id.id,
        )
