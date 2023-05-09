# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError

from odoo.addons.stock_analytic.tests.test_stock_picking import TestStockPicking


class TestStockLotAnalytic(TestStockPicking):
    def test_stock_lot_analytic_with_incoming_picking(self):
        self.product.tracking = "lot"
        picking = self._create_picking(
            self.location,
            self.dest_location,
            self.incoming_picking_type,
            self.analytic_distribution,
        )
        picking.action_confirm()
        picking.move_ids.quantity_done = 1
        with self.assertRaises(UserError):
            picking._action_done()
        picking.move_ids.move_line_ids[0].lot_name = "Test lot"
        picking.button_validate()
        lot_analytic = self.env["stock.lot"].search(
            [("product_id", "=", self.product.id), ("name", "=", "Test lot")]
        )
        self.assertEqual(lot_analytic.analytic_distribution, self.analytic_distribution)
