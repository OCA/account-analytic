# Copyright 2015 Antiun Ingenieria - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product1 = self.env['product.product'].create({
            'name': 'test product 01'})
        self.analytic_account1 = self.env['account.analytic.account'].create({
            'name': 'test analytic_account1'})
        self.analytic_account2 = self.env['account.analytic.account'].create({
            'name': 'test analytic_account2'})
        self.analytic_tag1 = self.env["account.analytic.tag"].create(
            {"name": "test analytic_tag1"}
        )
        self.analytic_tag2 = self.env["account.analytic.tag"].create(
            {"name": "test analytic_tag2"}
        )
        self.product2 = self.env['product.product'].create({
            'name': 'test product 02',
            'income_analytic_account_id': self.analytic_account1.id,
            'expense_analytic_account_id': self.analytic_account2.id,
            'income_analytic_tag_id': self.analytic_tag1.id,
            'expense_analytic_tag_id': self.analytic_tag2.id})
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner'})
        self.journal = self.env['account.journal'].create({
            'name': 'Test journal',
            'code': 'TEST',
            'type': 'general',
            'update_posted': True})
        self.account_type = self.env['account.account.type'].create({
            'name': 'Test account type',
            'type': 'other'})
        self.account = self.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': self.account_type.id})
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'journal_id': self.journal.id,
            'type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Test line',
                    'quantity': 1,
                    'price_unit': 50,
                    'account_id': self.account.id,
                    'product_id': self.product1.id,
                })
            ]
        })
        self.invoice_line = self.invoice.invoice_line_ids[0]

    def test_onchange_product_id(self):
        self.invoice_line.product_id = self.product2.id
        self.invoice_line._onchange_product_id()
        self.assertEqual(
            self.invoice_line.account_analytic_id.id,
            self.product2.income_analytic_account_id.id
        )
        self.assertEqual(
            self.invoice_line.analytic_tag_ids,
            self.product2.income_analytic_tag_id
        )

    def test_onchange_product_cumulative_analytic_tags(self):
        self.invoice_line.product_id = self.product2.id
        self.invoice_line.analytic_tag_ids |= self.analytic_tag2
        self.invoice_line._onchange_product_id()
        self.assertEqual(
            self.invoice_line.analytic_tag_ids,
            self.analytic_tag1 | self.analytic_tag2)

    def test_create_in(self):
        create_data = {
            'name': 'Test Line 2',
            'quantity': 1,
            'price_unit': 1,
            'account_id': self.account.id,
            'product_id': self.product2.id
        }
        invoice_line2 = self.env['account.invoice.line'].with_context(
            {'inv_type': 'in_invoice'}).create(create_data)
        self.assertEqual(invoice_line2.account_analytic_id.id,
                         self.product2.expense_analytic_account_id.id)
        self.assertEqual(
            invoice_line2.analytic_tag_ids,
            self.product2.expense_analytic_tag_id)

    def test_create_in_cumulative_analytic_tags(self):
        create_data = {
            'name': 'Test Line',
            'quantity': 1,
            'price_unit': 1,
            'account_id': self.account.id,
            'product_id': self.product2.id,
            'analytic_tag_ids': [(4, self.analytic_tag1.id)]
        }
        invoice_line = self.env['account.invoice.line'].with_context(
            {'inv_type': 'in_invoice'}).create(create_data)
        self.assertEqual(invoice_line.account_analytic_id.id,
                         self.product2.expense_analytic_account_id.id)
        self.assertEqual(
            invoice_line.analytic_tag_ids,
            self.analytic_tag1 | self.analytic_tag2)

    def test_create_in_cumulative_analytic_tags_2(self):
        create_data = {
            'name': 'Test Line',
            'quantity': 1,
            'price_unit': 1,
            'account_id': self.account.id,
            'product_id': self.product2.id,
            'analytic_tag_ids': [(4, self.analytic_tag1.id),
                                 (0, 0, {"name": "test analytic_tag3"})]
        }
        invoice_line = self.env['account.invoice.line'].with_context(
            {'inv_type': 'in_invoice'}).create(create_data)
        self.assertEqual(invoice_line.account_analytic_id.id,
                         self.product2.expense_analytic_account_id.id)
        self.assertEqual(
            set(invoice_line.analytic_tag_ids.mapped('name')),
            set(("test analytic_tag1", "test analytic_tag2",
                "test analytic_tag3")))

    def test_create_out(self):
        create_data = {
            'name': 'Test Line 3',
            'quantity': 1,
            'price_unit': 1,
            'account_id': self.account.id,
            'product_id': self.product2.id
        }
        invoice_line3 = self.env['account.invoice.line'].with_context(
            {'inv_type': 'out_invoice'}).create(create_data)
        self.assertEqual(invoice_line3.account_analytic_id.id,
                         self.product2.income_analytic_account_id.id)
        self.assertEqual(
            invoice_line3.analytic_tag_ids,
            self.product2.income_analytic_tag_id)

    def test_create_out_with_categ_tag(self):
        self.product2.income_analytic_tag_id = False
        create_data = {
            "name": "Test Line 1",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line1 = (
            self.env["account.invoice.line"]
                .with_context({"inv_type": "out_invoice"})
                .create(create_data)
        )
        self.assertFalse(invoice_line1.analytic_tag_ids)
        self.product2.categ_id = self.env["product.category"].create(
            {
                "name": "test category",
                "income_analytic_tag_id": self.analytic_tag1.id,
            }
        )
        create_data = {
            "name": "Test Line 2",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line2 = (
            self.env["account.invoice.line"]
                .with_context({"inv_type": "out_invoice"})
                .create(create_data)
        )
        self.assertEqual(
            invoice_line2.analytic_tag_ids, self.analytic_tag1
        )
        self.product2.categ_id.income_analytic_tag_id = False
        self.product2.categ_id.parent_id = self.env["product.category"].create(
            {
                "name": "test category",
                "income_analytic_tag_id": self.analytic_tag2.id,
            }
        )
        create_data = {
            "name": "Test Line 3",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line3 = (
            self.env["account.invoice.line"]
                .with_context({"inv_type": "out_invoice"})
                .create(create_data)
        )
        self.assertEqual(
            invoice_line3.analytic_tag_ids, self.analytic_tag2
        )

    def test_create_in_with_categ_tag(self):
        self.product2.expense_analytic_tag_id = False
        create_data = {
            "name": "Test Line 1",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line1 = (
            self.env["account.invoice.line"]
                .with_context({"inv_type": "in_invoice"})
                .create(create_data)
        )
        self.assertFalse(invoice_line1.analytic_tag_ids)
        self.product2.categ_id = self.env["product.category"].create(
            {
                "name": "test category",
                "expense_analytic_tag_id": self.analytic_tag1.id,
            }
        )
        create_data = {
            "name": "Test Line 2",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line2 = (
            self.env["account.invoice.line"]
                .with_context({"inv_type": "in_invoice"})
                .create(create_data)
        )
        self.assertEqual(
            invoice_line2.analytic_tag_ids, self.analytic_tag1
        )
        self.product2.categ_id.expense_analytic_tag_id = False
        self.product2.categ_id.parent_id = self.env["product.category"].create(
            {
                "name": "test category",
                "expense_analytic_tag_id": self.analytic_tag2.id,
            }
        )
        create_data = {
            "name": "Test Line 3",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line3 = (
            self.env["account.invoice.line"]
                .with_context({"inv_type": "in_invoice"})
                .create(create_data)
        )
        self.assertEqual(
            invoice_line3.analytic_tag_ids, self.analytic_tag2
        )

    def test_create_out_with_categ(self):
        self.product2.income_analytic_account_id = False
        create_data = {
            "name": "Test Line 1",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line1 = (
            self.env["account.invoice.line"]
            .with_context({"inv_type": "out_invoice"})
            .create(create_data)
        )
        self.assertFalse(invoice_line1.account_analytic_id)
        self.product2.categ_id = self.env["product.category"].create(
            {
                "name": "test category",
                "income_analytic_account_id": self.analytic_account1.id,
            }
        )
        create_data = {
            "name": "Test Line 2",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line2 = (
            self.env["account.invoice.line"]
            .with_context({"inv_type": "out_invoice"})
            .create(create_data)
        )
        self.assertEqual(
            invoice_line2.account_analytic_id, self.analytic_account1
        )
        self.product2.categ_id.income_analytic_account_id = False
        self.product2.categ_id.parent_id = self.env["product.category"].create(
            {
                "name": "test category",
                "income_analytic_account_id": self.analytic_account2.id,
            }
        )
        create_data = {
            "name": "Test Line 3",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line3 = (
            self.env["account.invoice.line"]
            .with_context({"inv_type": "out_invoice"})
            .create(create_data)
        )
        self.assertEqual(
            invoice_line3.account_analytic_id, self.analytic_account2
        )

    def test_create_in_with_categ(self):
        self.product2.expense_analytic_account_id = False
        create_data = {
            "name": "Test Line 1",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line1 = (
            self.env["account.invoice.line"]
            .with_context({"inv_type": "in_invoice"})
            .create(create_data)
        )
        self.assertFalse(invoice_line1.account_analytic_id)
        self.product2.categ_id = self.env["product.category"].create(
            {
                "name": "test category",
                "expense_analytic_account_id": self.analytic_account1.id,
            }
        )
        create_data = {
            "name": "Test Line 2",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line2 = (
            self.env["account.invoice.line"]
            .with_context({"inv_type": "in_invoice"})
            .create(create_data)
        )
        self.assertEqual(
            invoice_line2.account_analytic_id, self.analytic_account1
        )
        self.product2.categ_id.expense_analytic_account_id = False
        self.product2.categ_id.parent_id = self.env["product.category"].create(
            {
                "name": "test category",
                "expense_analytic_account_id": self.analytic_account2.id,
            }
        )
        create_data = {
            "name": "Test Line 3",
            "quantity": 1,
            "price_unit": 1,
            "account_id": self.account.id,
            "product_id": self.product2.id,
        }
        invoice_line3 = (
            self.env["account.invoice.line"]
            .with_context({"inv_type": "in_invoice"})
            .create(create_data)
        )
        self.assertEqual(
            invoice_line3.account_analytic_id, self.analytic_account2
        )
