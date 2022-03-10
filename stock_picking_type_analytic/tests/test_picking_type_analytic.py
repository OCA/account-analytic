# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_id = cls.env.ref("product.product_product_9")
        cls.uom_id = cls.env.ref("uom.product_uom_unit")
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "analytic accountic test"}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.analytic_account_id = cls.analytic_account

        cls.analytic_account_in = cls.env["account.analytic.account"].create(
            {"name": "analytic accountic test in"}
        )
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_in.analytic_account_id = cls.analytic_account_in

    @classmethod
    def _create_picking(cls):
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.picking_type_out.id,
            }
        )

    def test_default_picking_analytic(self):
        """
        Create a picking with a picking type that has an analytic account
        defined on it.
        """
        self._create_picking()
        self.assertEqual(
            self.picking.analytic_account_id, self.picking_type_out.analytic_account_id
        )

    def test_picking_analytic(self):
        """
        Create a picking with a picking type that has an analytic account
        defined on it.
        """
        picking = self.env["stock.picking"].new()
        picking.picking_type_id = self.picking_type_in
        picking._onchange_picking_type_id_analytic()

        self.assertEqual(
            picking.analytic_account_id, self.picking_type_in.analytic_account_id
        )
