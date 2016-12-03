# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceLine, self).setUp()
        self.product1 = self.env['product.product'].create({
            'name': 'test product 01'})
        self.product2 = self.env['product.product'].create({
            'name': 'test product 02',
            'income_analytic_account_id': self.env.ref(
                'account.analytic_in_house').id,
            'expense_analytic_account_id': self.env.ref(
                'account.analytic_online').id
        })
        self.partner = self.env.ref('base.res_partner_2')
        self.invoice = self.env['account.invoice'].create({
            'name': 'Test',
            'partner_id': self.partner.id,
            'account_id': self.env.ref('account.chart0').id
        })
        self.invoice_line = self.env['account.invoice.line'].create({
            'name': 'Test Line',
            'quantity': 1,
            'price_unit': 1,
            'product_id': self.product2.id
        })

    def test_product_id_change(self):
        res = self.invoice_line.product_id_change(
            self.product2.id, 1, partner_id=self.partner.id)
        self.assertEqual(res['value']['account_analytic_id'],
                         self.product2.income_analytic_account_id.id)
        self.invoice.type = 'in_invoice'
        res = self.invoice_line.product_id_change(
            self.product2.id, 1, partner_id=self.partner.id, type='in_invoice')
        self.assertEqual(res['value']['account_analytic_id'],
                         self.product2.expense_analytic_account_id.id)

    def test_create(self):
        self.assertEqual(self.invoice_line.account_analytic_id.id,
                         self.product2.income_analytic_account_id.id)
        create_data = {
            'name': 'Test Line 2',
            'quantity': 1,
            'price_unit': 1,
            'product_id': self.product2.id
        }
        invoice_line2 = self.env['account.invoice.line'].with_context(
            {'inv_type': 'in_invoice'}).create(create_data)
        self.assertEqual(invoice_line2.account_analytic_id.id,
                         self.product2.expense_analytic_account_id.id)
