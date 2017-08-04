# -*- coding: utf-8 -*-
# © 2015-2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceLine, self).setUp()
        self.account_model = self.env['account.account']
        self.product1 = self.env['product.product'].create({
            'name': 'test product 01'})
        self.product2 = self.env['product.product'].create({
            'name': 'test product 02',
            'income_analytic_account_id': self.env.ref(
                'analytic.analytic_administratif').id,
            'expense_analytic_account_id': self.env.ref(
                'analytic.analytic_commercial_marketing').id
        })
        self.partner = self.env.ref('base.res_partner_2')
        self.sale_journal = self.env['account.journal'].search([(
            'type', '=', 'sale')], limit=1)
        self.account_receivable = self.account_model.search([(
            'user_type_id',
            '=',
            self.env.ref('account.data_account_type_receivable').id)], limit=1)
        self.account_revenue = self.account_model.search([(
            'user_type_id',
            '=',
            self.env.ref('account.data_account_type_revenue').id)], limit=1)
        self.account_expense = self.account_model.search([(
            'user_type_id',
            '=',
            self.env.ref('account.data_account_type_expenses').id)], limit=1)
        self.invoice = self.env['account.invoice'].create({
            'name': 'Test',
            'partner_id': self.partner.id,
            'type': 'out_invoice',
            'journal_id': self.sale_journal.id,
            'account_id': self.account_receivable.id,
        })
        self.invoice_line = self.env['account.invoice.line'].create({
            'invoice_id': self.invoice.id,
            'name': 'Test Line',
            'quantity': 1,
            'price_unit': 1,
            'product_id': self.product2.id,
            'account_id': self.account_revenue.id,
        })

    def test_product_id_change(self):
        self.invoice_line.product_analytic_change()
        self.assertEqual(
            self.invoice_line.account_analytic_id,
            self.product2.income_analytic_account_id)

    def test_create(self):
        self.assertEqual(self.invoice_line.account_analytic_id.id,
                         self.product2.income_analytic_account_id.id)
        create_data = {
            'name': 'Test Line 2',
            'quantity': 1,
            'price_unit': 1,
            'product_id': self.product2.id,
            'account_id': self.account_expense.id,
        }
        invoice_line2 = self.env['account.invoice.line'].with_context(
            {'inv_type': 'in_invoice'}).create(create_data)
        self.assertEqual(invoice_line2.account_analytic_id.id,
                         self.product2.expense_analytic_account_id.id)
