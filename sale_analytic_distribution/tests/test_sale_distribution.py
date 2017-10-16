# -*- coding: utf-8 -*-
# Copyright 2017 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleDistribution(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleDistribution, cls).setUpClass()
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
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'partner_invoice_id': cls.partner.id,
            'partner_shipping_id': cls.partner.id,
            'order_line': [(0, 0, {
                'name': 'Product Test',
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'product_uom': cls.env.ref('product.product_uom_unit').id,
                'price_unit': 100.0,
            })],
        })
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

    def test_sale_distribution(self):
        self.order.order_line[0].analytic_distribution_id = \
            self.distribution.id
        self.order.action_confirm()
        # Create invoice
        inv_id = self.order.action_invoice_create()
        inv = self.invoice_model.browse(inv_id)
        # Check if analytic distribution are propagated to invoice
        self.assertEqual(inv.invoice_line_ids[0].analytic_distribution_id,
                         self.distribution)
