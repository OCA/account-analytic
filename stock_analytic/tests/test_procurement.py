# -*- coding: utf-8 -*-
# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProcurement(TransactionCase):

    def setUp(self):
        super(TestProcurement, self).setUp()
        self.stock_move_model = self.env['stock.move']
        self.procurement_order_model = self.env['procurement.order']
        self.procurement_rule_model = self.env['procurement.rule']
        self.warehouse_id = self.env.ref('stock.warehouse0')
        # Products
        self.product1 = self.env.ref('product.product_product_9')

        # Picking Type
        self.wh = self.env.ref('stock.warehouse0')
        self.stock_loc = self.env.ref('stock.stock_location_stock').id
        self.l2 = self.env['stock.location'].create({
            'location_id': self.stock_loc,
            'name': 'Shelf 1',
            'usage': 'internal'
        })
        self.picking_type = self.env.ref('stock.picking_type_internal')
        self.AA = self.env.ref('analytic.analytic_agrolait')
        self.rule = self._create_procurement_rule()
        self.procurement_order = self._create_procurement_order()

    def _create_procurement_rule(self):
        rule = self.procurement_rule_model. \
            create({'name': 'Procurement rule',
                    'action': 'move',
                    'location_id': self.stock_loc,
                    'location_src_id': self.l2.id,
                    'picking_type_id': self.picking_type.id,
                    })
        return rule

    def _create_procurement_order(self):
        # On change for warehouse_id
        new_line = self.procurement_order_model.new()
        new_line.warehouse_id = self.warehouse_id
        new_line.onchange_warehouse_id()
        location_id = new_line.location_id
        # On change for product_id
        new_line = self.procurement_order_model.new()
        new_line.product_id = self.product1.id
        new_line.onchange_product_id()
        product_uom = new_line.product_uom
        procurement = self.procurement_order_model. \
            create({'product_id': self.product1.id,
                    'product_uom': product_uom.id,
                    'product_qty': '10',
                    'name': 'Procurement Order',
                    'warehouse_id': self.warehouse_id.id,
                    'rule_id': self.rule.id,
                    'account_analytic_id': self.AA.id,
                    'location_id': location_id.id,
                    })
        procurement.run()
        procurement.check()
        return procurement

    def test_outgoing_picking_with_analytic(self):
        move = self.stock_move_model.search(
            [('procurement_id', '=', self.procurement_order.id)])
        self.assertEqual(move.analytic_account_id.id, self.AA.id)
