# Copyright 2015 Antiun Ingenieria - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import Command
from odoo.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.category = cls.env["product.category"].create(
            {
                "name": "Product Category",
            }
        )
        cls.default_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Default Plan",
                "company_id": False,
            }
        )
        cls.analytic_account1 = cls.env["account.analytic.account"].create(
            {
                "name": "test analytic_account1",
                "plan_id": cls.default_plan.id,
            }
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {
                "name": "test analytic_account2",
                "plan_id": cls.default_plan.id,
            }
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
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "lst_price": 20,
                "standard_price": 20,
                "income_analytic_account_id": False,
                "expense_analytic_account_id": False,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.journal_sale = cls.env["account.journal"].create(
            {"name": "Test journal sale", "code": "SALE0", "type": "sale"}
        )
        cls.journal_purchase = cls.env["account.journal"].create(
            {"name": "Test journal purchase", "code": "PURCHASE0", "type": "purchase"}
        )
        cls.account_in = cls.env["account.account"].create(
            {
                "name": "Test account IN",
                "code": "TESTIN",
                "account_type": "expense",
            }
        )
        cls.account_out = cls.env["account.account"].create(
            {
                "name": "Test account OUT",
                "code": "TESTOUT",
                "account_type": "income",
            }
        )

    def test_create_in(self):
        invoice = self.env["account.move"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_purchase.id,
                    "move_type": "in_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Test line",
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.account_in.id,
                                "product_id": self.product.id,
                            }
                        )
                    ],
                }
            ]
        )
        invoice_line = invoice.invoice_line_ids[0]
        analytic_account_id = [key for key in invoice_line.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
            self.product.expense_analytic_account_id.id,
        )

    def test_create_in_without(self):
        # Create an incoming invoice without analytic
        invoice = self.env["account.move"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_purchase.id,
                    "move_type": "in_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Test line",
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.account_in.id,
                                "product_id": self.product_1.id,
                            }
                        )
                    ],
                }
            ]
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertFalse(invoice_line.analytic_distribution)

    def test_create_in_category(self):
        # Create an incoming invoice with analytic on category
        self.category.expense_analytic_account_id = self.analytic_account2
        self.product_1.categ_id = self.category
        invoice = self.env["account.move"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_purchase.id,
                    "move_type": "in_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Test line",
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.account_in.id,
                                "product_id": self.product_1.id,
                            }
                        )
                    ],
                }
            ]
        )
        invoice_line = invoice.invoice_line_ids[0]
        analytic_account_id = [key for key in invoice_line.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
            self.analytic_account2.id,
        )

    def test_create_out(self):
        invoice = self.env["account.move"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_sale.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Test line",
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.account_out.id,
                                "product_id": self.product.id,
                            }
                        )
                    ],
                }
            ]
        )
        invoice_line = invoice.invoice_line_ids[0]
        analytic_account_id = [key for key in invoice_line.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
            self.product.income_analytic_account_id.id,
        )

    def test_create_out_without(self):
        # Create outgoing invoice without analytic
        invoice = self.env["account.move"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_sale.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Test line",
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.account_out.id,
                                "product_id": self.product_1.id,
                            }
                        )
                    ],
                }
            ]
        )
        invoice_line = invoice.invoice_line_ids[0]
        self.assertFalse(invoice_line.analytic_distribution)

    def test_create_out_category(self):
        # Create outgoing invoice without analytic
        self.category.income_analytic_account_id = self.analytic_account2
        self.product_1.categ_id = self.category
        invoice = self.env["account.move"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "journal_id": self.journal_sale.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Test line",
                                "quantity": 1,
                                "price_unit": 50,
                                "account_id": self.account_out.id,
                                "product_id": self.product_1.id,
                            }
                        )
                    ],
                }
            ]
        )
        invoice_line = invoice.invoice_line_ids[0]
        analytic_account_id = [key for key in invoice_line.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
            self.analytic_account2.id,
        )
