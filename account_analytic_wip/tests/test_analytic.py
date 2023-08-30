from odoo.tests import common


class TestAnalytic(common.TransactionCase):
    def setUp(self):
        super().setUp()
        analytic_plan = self.env["account.analytic.plan"].create(
            {"name": "Plan Test", "company_id": False}
        )
        # Analytic Account X
        self.analytic_x = self.env["account.analytic.account"].create(
            {"name": "Analytic X", "plan_id": analytic_plan.id}
        )
        # Accounts: Consume, WIP, Variance, Clear
        Account = self.env["account.account"]
        self.valuation_account = Account.create(
            {"code": "600010X", "name": "Valuation", "account_type": "expense"}
        )
        self.wip_account = Account.create(
            {"code": "600011X", "name": "WIP", "account_type": "expense"}
        )
        self.variance_account = Account.create(
            {"code": "600012X", "name": "Variance", "account_type": "expense"}
        )
        self.clear_account = Account.create(
            {"code": "600020X", "name": "Clear WIP", "account_type": "expense"}
        )
        # Product Category for the Activity Driven Costs
        self.costing_categ = self.env["product.category"].create(
            {
                "name": "Activity Driven Costs",
                "property_cost_method": "standard",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": self.valuation_account.id,
                "property_wip_account_id": self.wip_account.id,
                "property_variance_account_id": self.variance_account.id,
                "property_stock_account_output_categ_id": self.clear_account.id,
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
        # Total cost expeted is $25
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
        # Create a couple of Analytic Items for Engineering Work
        # 15 units at $25/unit = $375
        # split by $225 Labor + $150 Overhead
        AnalyticItem = self.env["account.analytic.line"]
        self.analytic_items = AnalyticItem.create(
            {
                "name": "Engineering work 1",
                "account_id": self.analytic_x.id,
                "product_id": self.engineering_product.id,
                "unit_amount": 10,
            }
        )
        self.analytic_items |= AnalyticItem.create(
            {
                "name": "Engineering work 2",
                "account_id": self.analytic_x.id,
                "product_id": self.engineering_product.id,
                "unit_amount": 5,
            }
        )
        self.tracking_items = self.analytic_x.analytic_tracking_item_ids
        self.tracking_engineering = self.tracking_items.filtered(
            lambda x: x.product_id == self.engineering_product
        )
        self.tracking_labor = self.tracking_items.filtered(
            lambda x: x.product_id == self.labor_driven_cost
        )

    def _get_account_balance(self, account, domain=None):
        JournalItems = self.env["account.move.line"]
        full_domain = [("account_id", "=", account.id)] + (domain or [])
        jis = JournalItems.search(full_domain)
        return sum(jis.mapped("balance"))

    def _get_account_balances(self, domain=None):
        return {
            "valuation": self._get_account_balance(self.valuation_account, domain),
            "wip": self._get_account_balance(self.wip_account, domain),
            "variance": self._get_account_balance(self.variance_account, domain),
            "clearing": self._get_account_balance(self.clear_account, domain),
        }

    def test_110_product_cost_driver_compute_cost(self):
        """Cost Driver unit cost is the sum of the driver costs"""
        # TODO: this should really be a analytic_activity_based_cost test...
        self.assertEqual(self.engineering_product.standard_price, 25.0)

    def test_200_analytic_item_tracking(self):
        # Expected Tracking Item with $25 * 15 U
        actual_amount = sum(self.tracking_items.mapped("actual_amount"))
        self.assertEqual(
            actual_amount,
            375.0,  # = ($10 + $15) * 15
            "Tracking total actual amount computation.",
        )
        # Expected line for Labor with amount 15 * 10
        self.assertEqual(
            self.tracking_labor.actual_amount,
            225.0,  # = $15 * 15
            "Tracking Labor actual amount computation.",
        )
        # No planned qty, means actual qty is WIP qty
        self.assertEqual(
            self.tracking_labor.wip_actual_amount,
            0.0,
            "With no planned amount, WIP is zero.",
        )
        self.assertEqual(
            self.tracking_labor.variance_actual_amount,
            225.0,
            "With no planned amount, Variance is the actual amount.",
        )

    def test_220_tracking_planned(self):
        # Set Planned Qty, means WIP and Variance are recomputed
        # for the activiy cost child lines
        # $225 value = $180 WIP Actual + $45 Variance
        self.tracking_engineering.planned_qty = 12
        self.assertEqual(
            self.tracking_labor.planned_amount,
            180.0,
            "Tracking child item Planned Amount recomputed when Planned Qty is set.",
        )
        self.assertEqual(
            self.tracking_labor.wip_actual_amount,
            180.0,
            "Tracking child item WIP recomputed when Planned Qty is set.",
        )
        self.assertEqual(
            self.tracking_labor.variance_actual_amount,
            45.0,
            "Tracking child item Variance recomputed when Planned Qty is set.",
        )

        # Post WIP to Accounting, check Journal Items
        # WIP Balance = 375
        # Variance not posted until the job is closed
        self.tracking_items.process_wip_and_variance()
        balances = self._get_account_balances()
        self.assertEqual(balances["wip"], 375.0)
        self.assertEqual(balances["variance"], 0.0)

        # Closing clears WIP and Posts variances
        # WIP Balance = 0
        # Variance Balance =75 (3 units excess * $25/unit)
        self.tracking_items.clear_wip_journal_entries()
        balances = self._get_account_balances()
        # WIP is not cleared at the moment. Reconsider?
        self.assertEqual(balances["wip"], 0.0)
        self.assertEqual(balances["variance"], 75.0)
