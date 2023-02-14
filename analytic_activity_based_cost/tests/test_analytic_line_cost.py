# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestAnalyticLineCost(common.TransactionCase):
    def setUp(self):
        super().setUp()
        analytic_plan = self.env["account.analytic.plan"].create(
            {"name": "Plan Test", "company_id": False}
        )
        # Analytic Account X
        self.analytic_x = self.env["account.analytic.account"].create(
            {"name": "Analytic X", "plan_id": analytic_plan.id}
        )
        self.cost_product_id = self.env.ref("analytic_activity_based_cost.labor_cost")
        self.product_id = self.env.ref("analytic_activity_based_cost.machine_cost_driver")
        self.ActivityLaborCostRule = self.env.ref("analytic_activity_based_cost.machine_cost_driver_labor_cost")
        self.ActivityOverheadCostRule = self.env.ref("analytic_activity_based_cost.machine_cost_driver_overhead_cost")

    def test_analytic_item_create(self):
        with self.assertRaises(ValidationError):
            self.cost_product_id.activity_cost_ids = [(6, 0, [self.ActivityLaborCostRule.id])]
        AnalyticItem1 = self.env["account.analytic.line"].create(
            {
                "name": "{}".format(
                    self.ActivityLaborCostRule.product_id.display_name or self.ActivityLaborCostRule.name
                ),
                "parent_id": False,
                "account_id": self.analytic_x.id,
                "activity_cost_id": self.ActivityLaborCostRule.id,
                "product_id": self.ActivityLaborCostRule.product_id.id,
                "product_uom_id": self.ActivityLaborCostRule.product_id.uom_id.id,
                "unit_amount": 0.0,
                "amount": 0.0,
            }
        )

        self.product_id.activity_cost_ids = [(6, 0, [self.ActivityOverheadCostRule.id])]
        AnalyticItem = self.env["account.analytic.line"].create(
            {
                "name": "{}".format(
                    self.ActivityOverheadCostRule.product_id.display_name or self.ActivityOverheadCostRule.name
                ),
                "parent_id": False,
                "account_id": self.analytic_x.id,
                "activity_cost_id": self.ActivityOverheadCostRule.id,
                "product_id": self.ActivityOverheadCostRule.product_id.id,
                "product_uom_id": self.ActivityOverheadCostRule.product_id.uom_id.id,
                "unit_amount": 0.0,
                "amount": 0.0,
            }
        )
