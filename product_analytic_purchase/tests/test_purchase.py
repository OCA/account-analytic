# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria - Javier Iniesta
# © 2017 Tecnativa - Luis Martínez
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPurchaseOrderLine(TransactionCase):

    def setUp(self):
        super(TestPurchaseOrderLine, self).setUp()
        self.product1 = self.env.ref('product.product_product_3')
        self.product2 = self.env.ref('product.service_order_01')
        self.assertTrue(self.product2.expense_analytic_account_id)
        self.po = self.env['purchase.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'name': self.product1.name,
                    'date_planned': '2017-07-17 12:42:12',
                    'product_qty': 12,
                    'product_uom': self.product1.uom_id.id,
                    'price_unit': 42,
                    })]
            })
        self.po_line1 = self.po.order_line[0]

    def test_onchange_product_id(self):
        self.po_line1.product_id = self.product2.id
        self.po_line1.onchange_product_id()
        self.assertEqual(
            self.po_line1.account_analytic_id.id,
            self.product2.expense_analytic_account_id.id)

    def test_create(self):
        pol_vals = {
            'product_id': self.product2.id,
            'name': self.product2.name,
            'date_planned': '2017-07-17 12:42:12',
            'product_qty': 42,
            'product_uom': self.product2.uom_id.id,
            'price_unit': 42,
            'order_id': self.po.id
            }
        po_line2 = self.env['purchase.order.line'].create(pol_vals)
        self.assertEqual(
            po_line2.account_analytic_id.id,
            self.product2.expense_analytic_account_id.id)
