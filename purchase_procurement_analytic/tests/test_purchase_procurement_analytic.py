# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestPurchaseProcurementAnalytic(TransactionCase):
    """ Use case : Prepare some data for current test case """
    def setUp(self):
        super(TestPurchaseProcurementAnalytic, self).setUp()

        self.product = self.env.ref('product.product_product_8')
        self.analytic_account = self.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
            'type': 'contract',
        })

        procur_vals = {
            'name': 'Procurement test',
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'route_ids': [
                (6, 0, [self.env.ref('purchase.route_warehouse0_buy').id])],
            'product_qty': 1.0,
        }
        self.procurement_1 = self.env['procurement.order'].create(procur_vals)

        procur_vals['account_analytic_id'] = self.analytic_account.id
        self.procurement_2 = self.env['procurement.order'].create(procur_vals)

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
        po = self.procurement_2.purchase_id
        # Confirm PO to create stock.move
        po.signal_workflow("purchase_confirm")
        stock_move = self.procurement_2.purchase_line_id.move_ids[0]
        procur_vals = self.env['stock.move']._prepare_procurement_from_move(
            stock_move)
        self.assertEqual(
            procur_vals['account_analytic_id'], self.analytic_account.id)
