# Copyright (C) 2024 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInventoryAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_id = cls.env.ref("product.product_product_9")
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Analytic Test", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution = {str(analytic_account.id): 100}
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Analytic",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

    def test_inventory_analytic(self):
        """Check that inventory adjustments add analytic distribution to moves"""
        # make some stock
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 100
        )

        # check that the quant exists
        inventory_quant = self.env["stock.quant"].search(
            [
                ("location_id", "=", self.stock_location.id),
                ("product_id", "=", self.product.id),
            ]
        )

        self.assertEqual(len(inventory_quant), 1)
        self.assertEqual(inventory_quant.quantity, 100)
        self.assertEqual(inventory_quant.inventory_quantity, 0)

        # add analytic distribution and counted quantity
        inventory_quant.write(
            {
                "inventory_quantity": 70,
                "analytic_distribution": self.analytic_distribution,
            }
        )

        # apply inventory
        inventory_quant.action_apply_inventory()

        # check that inventory count changed
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.stock_location
            ),
            70.0,
        )

        # check that analytic distribution on the quant is cleared
        self.assertFalse(inventory_quant.analytic_distribution)

        # check that analytic distribution carried to the stock move
        new_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        self.assertEqual(len(new_move), 1)
        self.assertEqual(new_move.analytic_distribution, self.analytic_distribution)
