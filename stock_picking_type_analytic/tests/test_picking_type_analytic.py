# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_analytic.tests.common import CommonStockPicking


class TestStockAnalytic(CommonStockPicking):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_id = cls.env.ref("uom.product_uom_unit")
        cls.outgoing_picking_type.analytic_distribution = cls.analytic_distribution
        cls.analytic_account_in = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account IN", "plan_id": cls.analytic_plan.id}
        )
        cls.analytic_distribution_in = {
            str(cls.analytic_account.id): 10.0,
            str(cls.analytic_account_in.id): 90.0,
        }

        cls.incoming_picking_type.analytic_distribution = cls.analytic_distribution_in

    @classmethod
    def _create_picking(cls):
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.location.id,
                "location_dest_id": cls.dest_location.id,
                "picking_type_id": cls.outgoing_picking_type.id,
            }
        )

    def test_default_picking_analytic(self):
        """
        Create a picking with a picking type that has an analytic account
        defined on it.
        """
        self._create_picking()
        self.assertEqual(
            self.picking.analytic_distribution,
            self.outgoing_picking_type.analytic_distribution,
        )

    def test_picking_analytic(self):
        """
        Create a picking with a picking type that has an analytic account
        defined on it.
        """
        picking = self.env["stock.picking"].new()
        picking.picking_type_id = self.incoming_picking_type
        picking._onchange_picking_type_id_analytic()

        self.assertEqual(
            picking.analytic_distribution,
            self.incoming_picking_type.analytic_distribution,
        )
