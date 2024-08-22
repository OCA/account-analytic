# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_id = cls.env.ref("product.product_product_9")
        cls.uom_id = cls.env.ref("uom.product_uom_unit")
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        analytic_account = cls.env["account.analytic.account"].create(
            {"name": "analytic account test", "plan_id": analytic_plan.id}
        )
        analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "analytic account test 2", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution = {str(analytic_account.id): 100}
        cls.analytic_distribution_2 = {str(analytic_account_2.id): 100}
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "move test",
                            "product_id": cls.product_id.id,
                            "product_uom": cls.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )

    def test_inverse_analytic_distribution(self):
        """Set analytic distribution on picking
        Check analytic distribution on line is set
        """
        picking = self.picking
        self.assertTrue(picking.move_ids_without_package)
        self.assertNotEqual(
            picking.move_ids_without_package[0].analytic_distribution,
            self.analytic_distribution,
        )
        picking.analytic_distribution = self.analytic_distribution
        self.assertEqual(
            picking.move_ids_without_package[0].analytic_distribution,
            self.analytic_distribution,
        )

    def test_compute_analytic_distribution(self):
        """Set analytic distribution on move
        Check analytic distribution on picking is set
        """
        picking = self.picking
        self.assertTrue(picking.move_ids_without_package)
        self.assertNotEqual(
            picking.move_ids_without_package[0].analytic_distribution,
            self.analytic_distribution,
        )
        picking.move_ids_without_package.write(
            {
                "analytic_distribution": self.analytic_distribution,
            }
        )
        self.assertEqual(
            picking.analytic_distribution,
            self.analytic_distribution,
        )

    def test_compute_no_move(self):
        """
        Set analytic distribution on void picking
        """
        picking = self.picking
        picking.move_ids_without_package = False
        self.picking.analytic_distribution = self.analytic_distribution
        self.assertEqual(picking.analytic_distribution, self.analytic_distribution)
        self.assertEqual(
            picking.original_analytic_distribution, self.analytic_distribution
        )

    def test_compute_different_analytic_distribution(self):
        """Add a move with another analytic distribution
        Check if no analytic distribution is set
        """
        picking = self.picking
        picking.move_ids_without_package.write(
            {
                "analytic_distribution": self.analytic_distribution,
            }
        )
        self.picking.write(
            {
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": "move test 2",
                            "product_id": self.product_id.id,
                            "product_uom": self.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                            "analytic_distribution": self.analytic_distribution_2,
                        },
                    )
                ]
            }
        )
        self.assertFalse(
            picking.analytic_distribution,
        )
