# -*- coding: utf-8 -*-
# Copyright 2017 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from openerp.tests import common


class TestPurchaseDistribution(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseDistribution, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.account1 = cls.env['account.analytic.account'].create({
            'name': 'Test account #1',
        })
        cls.account2 = cls.env['account.analytic.account'].create({
            'name': 'Test account #2',
        })
        order_vals = {
            'partner_id': cls.partner.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'pricelist_id': cls.env.ref('product.list0').id,
            'order_line': [(0, 0, {
                'name': 'Product Test',
                'product_id': cls.product.id,
                'product_qty': 1,
                'product_uom': cls.env.ref('product.product_uom_unit').id,
                'price_unit': 100.0,
                'date_planned': datetime.today().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT),
            })],
        }
        cls.order = cls.env['purchase.order'].create(order_vals)
        cls.invoice_model = cls.env['account.invoice']
        cls.distribution = cls.env['account.analytic.distribution'].create({
            'name': 'Test distribution',
            'rule_ids': [
                (0, 0, {
                    'sequence': 10,
                    'percent': 75.00,
                    'analytic_account_id': cls.account1.id,
                }),
                (0, 0, {
                    'sequence': 20,
                    'percent': 25.00,
                    'analytic_account_id': cls.account2.id,
                }),
            ]
        })

    def test_purchase_distribution(self):
        self.order.order_line[0].analytic_distribution_id = \
            self.distribution.id
        self.order.action_picking_create()
        self.order.signal_workflow('confirm')
        self.picking = self.order.picking_ids[0]
        self.picking.force_assign()
        self.picking.pack_operation_ids.write({'qty_done': 1.0})
        self.picking.do_transfer()

        # Create invoice
        self.order.order_line.action_confirm()
        self.order.write({'invoice_method': 'manual'})
        self.order.view_invoice()

        # Check if analytic distribution are propagated to invoice
        invoice = self.order.invoice_ids
        self.assertTrue(invoice)
        self.assertEqual(invoice.invoice_line[0].analytic_distribution_id,
                         self.distribution)
