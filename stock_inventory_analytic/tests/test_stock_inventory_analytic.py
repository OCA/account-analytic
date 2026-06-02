# Copyright 2019 ForgeFlow S.L.
# Copyright 2019 brain-tec AG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.fields import Command
from odoo.tests import Form, TransactionCase


class TestInventoryAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        product = cls.env["product.product"]
        location = cls.env["stock.location"]
        cls.product = product.create(
            {
                "name": "Product A",
                "is_storable": True,
            }
        )
        cls.warehouse = location.create(
            {
                "name": "Warehouse",
                "usage": "internal",
            }
        )
        cls.stock = location.create(
            {
                "name": "Stock",
                "usage": "internal",
                "location_id": cls.warehouse.id,
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
        """Create a quant and apply physical inventory to it hen check that the
        analytic distribution is propagated in the corresponding `stock.move`.
        """
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock.id,
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

    def test_inventory_adjustment_analytic(self):
        """Create a quant with and apply physical inventory to it specifying an
        analytic distribution other than the default one then check that this
        analytic distribution is propagated in the corresponding `stock.move`.
        """
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock.id,
                "inventory_quantity": 1,
            }
        )
        form_wizard = Form(
            self.env["stock.inventory.adjustment.name"].with_context(
                default_quant_ids=quant.ids
            )
        )
        form_wizard.inventory_adjustment_name = "Inventory Adjustment - Test"
        form_wizard.analytic_distribution = self.analytic_distribution_12
        form_wizard.save().action_apply()
        moves = self.env["stock.move"].search(
            [("reference", "=", "Inventory Adjustment - Test")], limit=1
        )
        self.assertEqual(moves[0].analytic_distribution, self.analytic_distribution_12)
