# Copyright 2015 Antiun Ingenieria - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):
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
        cls.analytic_tag1 = cls.env["account.analytic.tag"].create(
            {"name": "test analytic_tag1"}
        )
        cls.analytic_tag2 = cls.env["account.analytic.tag"].create(
            {"name": "test analytic_tag2"}
        )
        cls.analytic_tag3 = cls.env["account.analytic.tag"].create(
            {"name": "test analytic_tag3"}
        )
        cls.product_categ = cls.env["product.category"].create(
            {
                "name": "test product categoty",
                "income_analytic_account_id": cls.analytic_account1.id,
                "income_analytic_account_tag_ids": [(6, 0, [cls.analytic_tag1.id])],
                "expense_analytic_account_tag_ids": [
                    (6, 0, [cls.analytic_tag1.id, cls.analytic_tag2.id])
                ],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product",
                "lst_price": 50,
                "standard_price": 50,
                "categ_id": cls.product_categ.id,
                "expense_analytic_account_id": cls.analytic_account2.id,
                "income_analytic_account_tag_ids": [(6, 0, [cls.analytic_tag2.id])],
                "expense_analytic_account_tag_ids": [
                    (6, 0, [cls.analytic_tag2.id, cls.analytic_tag3.id])
                ],
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product no default analytic",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test journal sale", "code": "SALE0", "type": "sale"}
        )
        cls.journal_general = cls.env["account.journal"].create(
            {"name": "Test journal sale", "code": "misc", "type": "general"}
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
        self.assertEqual(
            invoice_line.analytic_tag_ids,
            self.product.expense_analytic_account_tag_ids
            | self.product.categ_id.expense_analytic_account_tag_ids,
        )
        invoice_line2 = self.env["account.move.line"].create(
            {
                "move_id": invoice.id,
                "name": "Test no default analytic",
                "quantity": 1,
                "account_id": self.account.id,
                "product_id": self.product2.id,
            }
        )
        invoice_line2._onchange_product_id()
        self.assertEqual(
            len(invoice_line2.analytic_account_id),
            0,
        )
        self.assertEqual(
            len(invoice_line2.analytic_tag_ids),
            0,
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
            self.product.categ_id.income_analytic_account_id.id,
        )
        self.assertEqual(
            invoice_line.analytic_tag_ids,
            self.product.income_analytic_account_tag_ids
            | self.product.categ_id.income_analytic_account_tag_ids,
        )

    def test_entry(self):
        entry = self.env["account.move"].create(
            {
                "journal_id": self.journal_general.id,
                "move_type": "entry",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "account_id": self.account.id,
                        },
                    )
                ],
            }
        )
        entry_line = entry.line_ids[0]
        entry_line._onchange_product_id()
        self.assertEqual(
            len(entry_line.analytic_account_id),
            0,
        )
        self.assertEqual(
            len(entry_line.analytic_tag_ids),
            0,
        )
