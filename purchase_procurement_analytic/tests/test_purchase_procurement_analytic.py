# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.SavepointCase):
    """Use case : Prepare some data for current test case"""

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseProcurementAnalytic, cls).setUpClass()

        cls.product = cls.env.ref('product.product_product_8')
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
        })
        cls.buy_rule = cls.env['procurement.rule'].search([
            ('action', '=', 'buy'),
            ('warehouse_id', '=', cls.env.ref('stock.warehouse0').id)])
        procur_vals = {
            'name': 'Procurement test',
            'product_id': cls.product.id,
            'product_uom': cls.product.uom_id.id,
            'warehouse_id': cls.env.ref('stock.warehouse0').id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'route_ids': [
                (6, 0, [cls.env.ref('purchase.route_warehouse0_buy').id])],
            'rule_id': cls.buy_rule.id,
            'product_qty': 1.0,
        }
        cls.procurement_1 = cls.env['procurement.order'].with_context(
            {'no_reset_password': True, 'mail_create_nosubscribe': True}
        ).create(procur_vals)

        procur_vals['account_analytic_id'] = cls.analytic_account.id
        procur_vals.update({'product_qty': 2})
        cls.procurement_2 = cls.env['procurement.order'].with_context(
            {'no_reset_password': True, 'mail_create_nosubscribe': True}
        ).create(procur_vals)

    def test_procurement_to_purchase(self):
        # Run procurement
        self.procurement_1.run()
        self.procurement_2.run()
        self.assertTrue(
            self.procurement_2.purchase_id)
        # Make sure that PO line have analytic account
        self.assertEqual(
            self.procurement_2.purchase_line_id.account_analytic_id.id,
            self.analytic_account.id)
        # Create procurement from move
        self.purchase = self.procurement_2.purchase_id
        self.assertEqual(self.purchase.order_line[0].state, 'draft')
        self.purchase.button_confirm()
        self.picking = self.purchase.picking_ids[0]
        self.move = self.picking.move_lines[0]
        self.move.procure_method = 'make_to_order'
        self.move.action_confirm()
        self.assertEqual(self.move.state, 'waiting')
        self.assertEqual(self.purchase.order_line[0].state, 'purchase')
