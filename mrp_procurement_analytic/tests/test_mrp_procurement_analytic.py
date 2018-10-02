# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestMrpAnalytic(common.TransactionCase):

    def setUp(self):
        super(TestMrpAnalytic, self).setUp()
        self.route_mrp = self.env.ref('mrp.route_warehouse0_manufacture')
        self.route_mto = self.env.ref('stock.route_warehouse0_mto')
        self.bom_obj = self.env['mrp.bom']
        vals = {
            'name': 'Component 1',
            'sale_ok': False,
            'purchase_ok': True,
            'type': 'product',
        }
        self.composant_1 = self.env['product.product'].create(vals)
        vals = {
            'name': 'Component 2',
            'sale_ok': False,
            'purchase_ok': True,
            'type': 'product',
        }
        self.composant_2 = self.env['product.product'].create(vals)
        vals = {
            'name': 'MRP Product',
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'product',
            'list_price': 150,
            'route_ids': [
                (6, 0, [self.route_mrp.id, self.route_mto.id]),
            ],
        }
        self.product = self.env['product.product'].create(vals)

        vals = {
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'type': 'normal',
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.composant_1.id,
                    'product_qty': 1.0,
                }),
                (0, 0, {
                    'product_id': self.composant_2.id,
                    'product_qty': 2.0}),
            ],
        }
        self.bom = self.env['mrp.bom'].create(vals)

    def test_mrp_analytic(self):
        self.move_obj = self.env['stock.move']
        project_1 = self.env.ref('analytic.analytic_agrolait')
        vals = {
            'name': 'Procurement 1',
            'product_id': self.product.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_qty': 1.0,
            'account_analytic_id': project_1.id,
            'product_uom': self.env.ref('product.product_uom_unit').id,
        }
        self.env['procurement.order'].create(vals)

        production = self.env['mrp.production'].search([
            ('analytic_account_id', '=', project_1.id)
        ])
        self.assertEquals(
            1,
            len(production)
        )

        moves = self.move_obj.search([
            ('analytic_account_id', '=', project_1.id)
        ])
        self.assertEqual(3, len(moves))
