# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestInventoryWarehouseAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        product = cls.env["product.product"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product = product.create(
            {
                "name": "Product A",
                "is_storable": True,
            }
        )
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        analytic_account_1 = cls.env["account.analytic.account"].create(
            {"name": "AA 1", "plan_id": analytic_plan.id}
        )
        analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "AA 2", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution_1 = {str(analytic_account_1.id): 100}
        cls.analytic_distribution_12 = {
            str(analytic_account_1.id): 30,
            str(analytic_account_2.id): 70,
        }
        cls.env.user.company_id.write(
            {
                "analytic_distribution": cls.analytic_distribution_1,
            }
        )
        group = cls.env.ref("analytic.group_analytic_accounting")
        group.user_ids = [Command.link(cls.env.user.id)]

    def test_inventory_adjustment_analytic_default(self):
        """Default is still working if no warehouse analytic is provided.
        Create a quant and apply physical inventory to it hen check that the
        analytic distribution is propagated in the corresponding `stock.move`.
        """
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "inventory_quantity": 1,
            }
        )
        form_wizard = Form(
            self.env["stock.inventory.adjustment.name"].with_context(
                default_quant_ids=quant.ids
            )
        )
        form_wizard.inventory_adjustment_name = "Inventory Adjustment - Test default"
        form_wizard.save().action_apply()
        moves = self.env["stock.move"].search(
            [("reference", "=", "Inventory Adjustment - Test default")], limit=1
        )
        self.assertEqual(moves[0].analytic_distribution, self.analytic_distribution_1)

    def test_inventory_adjustment_analytic_warehouse(self):
        """Add an analytic distribution to the inventory warehouse.
        Create a quant and apply physical inventory to it then check that the warehouse
        analytic distribution is propagated in the corresponding `stock.move`.
        """
        self.stock_location.warehouse_id.analytic_distribution = (
            self.analytic_distribution_12
        )
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "inventory_quantity": 1,
            }
        )
        form_wizard = Form(
            self.env["stock.inventory.adjustment.name"].with_context(
                default_quant_ids=quant.ids
            )
        )
        form_wizard.inventory_adjustment_name = "Inventory Adjustment - Test Warehouse"
        form_wizard.save().action_apply()
        moves = self.env["stock.move"].search(
            [("reference", "=", "Inventory Adjustment - Test Warehouse")], limit=1
        )
        self.assertEqual(moves[0].analytic_distribution, self.analytic_distribution_12)
