# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_id = cls.env.ref("product.product_product_9")
        cls.uom_id = cls.env.ref("uom.product_uom_unit")
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "analytic account test"}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": "move test",
                            "product_id": cls.product_id.id,
                            "product_uom": cls.uom_id.id,
                        },
                    )
                ],
            }
        )

    def test_inverse_analytic_account_id(self):
        """Set analytic account on picking
        Check analytic account on line is set
        """
        picking = self.picking
        self.assertNotEqual(len(picking.move_ids_without_package), 0)
        self.assertNotEqual(
            picking.move_ids_without_package[0].analytic_account_id,
            self.analytic_account,
        )
        picking.analytic_account_id = self.analytic_account.id
        self.assertEqual(
            picking.move_ids_without_package[0].analytic_account_id,
            self.analytic_account,
        )

    def test_compute_analytic_account_id(self):
        """Set analytic account on move
        Check analytic account on picking is set
        """
        picking = self.picking
        self.assertNotEqual(len(picking.move_ids_without_package), 0)
        self.assertNotEqual(
            picking.move_ids_without_package[0].analytic_account_id,
            self.analytic_account,
        )
        picking.move_ids_without_package.write(
            {
                "analytic_account_id": self.analytic_account.id,
            }
        )
        self.assertEqual(
            picking.analytic_account_id,
            self.analytic_account,
        )

    def test_compute_no_move(self):
        """
        Set analytic account on void picking
        """
        picking = self.picking
        picking.move_ids_without_package = False
        self.picking.analytic_account_id = self.analytic_account
        self.assertEqual(picking.analytic_account_id, self.analytic_account)
        self.assertEqual(picking.original_analytic_account_id, self.analytic_account)

    def test_compute_different_analytic_account_id(self):
        """
        Add a move with another analytic account
        Check if no analytic account is set
        """
        picking = self.picking
        picking.move_ids_without_package.write(
            {
                "analytic_account_id": self.analytic_account.id,
            }
        )
        self.picking.write(
            {
                "move_ids_without_package": [
                    (
                        0,
                        0,
                        {
                            "name": "move test 2",
                            "product_id": self.product_id.id,
                            "product_uom": self.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ]
            }
        )
        self.assertFalse(
            picking.analytic_account_id,
        )
