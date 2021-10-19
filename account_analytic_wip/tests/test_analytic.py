from odoo import exceptions
from odoo.tests import common


class TestAnalytic(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # Analytic Account X
        self.analytic_x = self.env["account.analytic.account"].create(
            {"name": "Analytic X"}
        )
        # Accounts: Consume, WIP, Variance
        Account = self.env["account.account"]
        account_vals = {
            "code": "600010X",
            "name": "Costing Consumed",
            "user_type_id": self.env.ref("account.data_account_type_expenses").id,
        }
        self.consume_account = Account.create(account_vals)
        self.wip_account = self.consume_account.copy(
            {"code": "600011X", "name": "Costing WIP"}
        )
        self.variance_account = self.consume_account.copy(
            {"code": "600012X", "name": "Costing Variance"}
        )
        # Product Category for the Driven Costs
        self.costing_categ = self.env["product.category"].create(
            {
                "name": "Driven Costs",
                "property_cost_method": "standard",
                "property_valuation": "real_time",
                "property_wip_account_id": self.wip_account.id,
                "property_variance_account_id": self.variance_account.id,
            }
        )
        # Products: driven costs
        Product = self.env["product.product"]
        self.labor_driven_cost = Product.create(
            {
                "name": "Labor Cost",
                "type": "service",
                "categ_id": self.costing_categ.id,
                "standard_price": 15.0,
            }
        )
        self.overhead_driven_cost = Product.create(
            {
                "name": "Overhead Cost",
                "type": "service",
                "categ_id": self.costing_categ.id,
                "standard_price": 10.0,
            }
        )
        # Products: cost driver Engineering work,
        # driving Labor and Overhead costs
        self.engineering_product = Product.create(
            {
                "name": "Engineering (cost driver)",
                "type": "service",
                "categ_id": self.costing_categ.id,
                "is_cost_type": True,
            }
        )
        ActivityCostRule = self.env["activity.cost.rule"]
        ActivityCostRule.create(
            {
                "name": "Labor",
                "parent_id": self.engineering_product.id,
                "product_id": self.labor_driven_cost.id,
            }
        )
        ActivityCostRule.create(
            {
                "name": "Overhead",
                "parent_id": self.engineering_product.id,
                "product_id": self.overhead_driven_cost.id,
            }
        )

    def test_100_categ_config_complete(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env["product.category"].create(
                {
                    "name": "Engineer to Order",
                    "property_cost_method": "standard",
                    "property_valuation": "real_time",
                    "property_wip_account_id": self.wip_account.id,
                    "property_variance_account_id": self.variance_account.id,
                }
            )

    def test_110_product_cost_driver_compute_cost(self):
        """Cost Driver unit cost is the sum of the driver costs"""
        # TODO: this should really be a analytic_activity_based_cost test...
        self.assertEqual(self.engineering_product.standard_price, 25.0)

    def test_200_analytic_item_create(self):
        AnalyticItem = self.env["account.analytic.line"]
        AnalyticItem.create(
            {
                "name": "Engineering work 1",
                "account_id": self.analytic_x.id,
                "product_id": self.engineering_product.id,
                "unit_amount": 10,
            }
        )
        tracking_items = self.analytic_x.analytic_tracking_item_ids
        AnalyticItem.create(
            {
                "name": "Engineering work 2",
                "account_id": self.analytic_x.id,
                "product_id": self.engineering_product.id,
                "unit_amount": 5,
            }
        )

        # Expected Tracking Item with $25 * 15 U
        tracking_items = self.analytic_x.analytic_tracking_item_ids
        actual_amount = sum(tracking_items.mapped("actual_amount"))
        self.assertEqual(
            actual_amount,
            375.0,
            "Tracking total actual amount computation.",
        )

        # Expected line for Labor with amount 15 * 10
        tracking_labor = tracking_items.filtered(
            lambda x: x.product_id == self.labor_driven_cost
        )
        self.assertEqual(
            tracking_labor.actual_amount,
            225.0,
            "Tracking Labor actual amount computation.",
        )

        # No planned qty, means actual qty is WIP qty
        self.assertEqual(
            tracking_labor.wip_actual_amount,
            225.0,
            "Tracking Labor WIP amount computation when no Planned Qty.",
        )

        # Set Planned Qty, means WIP and Variance are recomputed
        # for the activiy cost child lines
        tracking_engineering = tracking_items.filtered(
            lambda x: x.product_id == self.engineering_product
        )
        tracking_engineering.planned_qty = 12
        self.assertEqual(
            tracking_labor.planned_amount,
            180.0,
            "Tracking child item Planned Amount recomputed when Planned Qty is set.",
        )
        self.assertEqual(
            tracking_labor.wip_actual_amount,
            180.0,
            "Tracking child item WIP recomputed when Planned Qty is set.",
        )
        self.assertEqual(
            tracking_labor.variance_actual_amount,
            45.0,
            "Tracking child item Variance recomputed when Planned Qty is set.",
        )

        # Post to accounting, generates missing Variance JEs,
        # but in this case those were already generated
        # Closing clear the WIP balance
        tracking_items.process_wip_and_variance(close=True)
        jis = tracking_items.mapped("account_move_ids.line_ids")
        jis_wip = jis.filtered(lambda x: x.account_id == self.wip_account)
        wip_amount = sum(jis_wip.mapped("balance"))
        self.assertEqual(wip_amount, 0.0)

        jis_var = jis.filtered(lambda x: x.account_id == self.variance_account)
        var_amount = sum(jis_var.mapped("balance"))
        self.assertEqual(var_amount, 75.0)
