# -*- coding: utf-8 -*-
# © 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrderLine(TransactionCase):

    def setUp(self):
        super(TestSaleOrderLine, self).setUp()
        self.product = self.env.ref('product.service_order_01')
        self.assertTrue(self.product.income_analytic_account_id)
        self.order = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'product_uom_qty': 12,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': 42,
                    })]
            })

    def test_invoice(self):
        self.order.action_confirm()
        invoice_ids = self.order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_ids[0])
        self.assertEqual(
            invoice.invoice_line_ids[0].account_analytic_id.id,
            self.product.income_analytic_account_id.id)
