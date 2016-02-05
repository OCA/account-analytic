# -*- coding: utf-8 -*-
# © 2013 Julius Network Solutions
# © 2015 Clear Corp
# © 2016 Andhitia Rama <andhitia.r@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime


class TestStockPicking(TransactionCase):

    def setUp(self):
        super(TestStockPicking, self).setUp()

        self.product = self.env.ref('product.product_product_4')
        self.product.update({'valuation': 'real_time'})
        self.product_categ = self.env.ref('product.ipad')
        self.valuation_account = self.env.ref('account.stk')
        self.stock_account = self.env.ref('account.xfa')
        self.stock_journal = self.env.ref('stock_account.stock_journal')
        self.analytic_journal = self.env.ref('account.sit')
        self.analytic_account = self.env.ref(
            'account.analytic_project_1_development')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.location = self.warehouse.lot_stock_id
        self.dest_location = self.env.ref('stock.stock_location_customers')
        self.picking_type = self.env.ref('stock.picking_type_out')

        self.stock_journal.update({
            'analytic_journal_id': self.analytic_journal.id
        })

        self.product_categ.update({
            'property_stock_valuation_account_id': self.valuation_account.id,
            'property_stock_account_input_categ': self.stock_account.id,
            'property_stock_account_output_categ': self.stock_account.id,
        })

    def test_stock_picking(self):
        picking_data = {
            'picking_type_id': self.picking_type.id,
            'move_type': 'direct',
            }

        self.picking = self.env['stock.picking'].create(picking_data)

        move_data = {
            'picking_id': self.picking.id,
            'product_id': self.product.id,
            'location_id': self.location.id,
            'location_dest_id': self.dest_location.id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_expected': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'invoice_state': 'none',
            'name': self.product.name,
            'procure_method': 'make_to_stock',
            'product_uom': self.product.uom_id.id,
            'product_uom_qty': 1.0,
            'account_analytic_id': self.analytic_account.id
            }

        self.move = self.env['stock.move'].create(move_data)

        self.picking.action_confirm()
        self.assertEqual(self.picking.state, 'confirmed')

        self.picking.force_assign()
        self.assertEqual(self.picking.state, 'assigned')

        self.picking.action_done()
        self.assertEqual(self.picking.state, 'done')

        criteria1 = [['ref', '=', self.picking.name]]
        acc_moves = self.env['account.move'].search(criteria1)
        self.assertGreater(len(acc_moves), 0)

        criteria2 = [['move_id.ref', '=', self.picking.name]]
        acc_lines = self.env['account.move.line'].search(criteria2)
        for acc_line in acc_lines:
            self.assertEqual(
                acc_line.analytic_account_id.id,
                self.move.account_analytic_id.id)
