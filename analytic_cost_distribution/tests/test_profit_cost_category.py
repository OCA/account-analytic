# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.analytic_cost_distribution.tests.common import (
    CostDistributionCommon,
)


@tagged("post_install", "-at_install")
class TestProfitCostCategory(CostDistributionCommon):
    def test_other(self):
        line = self._create_profit_line(self.profit_account_a, 100, "2025-01-15")
        self.assertEqual(line.profit_cost_category, "other")

    def test_costs_distribution(self):
        operation = self.Operation.create(
            {
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
                "distribution_date": "2025-01-31",
            }
        )
        line = self.AnalyticLine.create(
            {
                "name": "Distributed",
                "date": "2025-01-31",
                "account_id": self.profit_account_a.id,
                "amount": -50.0,
                "indirect_cost_distribution_operation_id": operation.id,
            }
        )
        self.assertEqual(line.profit_cost_category, "costs_distribution")

    def test_timesheet(self):
        project = self.env["project.project"].create(
            {
                "name": "Test project",
                "allow_timesheets": True,
                "account_id": self.profit_account_a.id,
            }
        )
        line = self._create_timesheet_line(
            self.profit_account_a, 8.0, "2025-01-15", project
        )
        self.assertEqual(line.profit_cost_category, "timesheet")

    def test_category_is_editable(self):
        """The field is readonly=False and can be overridden."""
        line = self._create_profit_line(self.profit_account_a, 100, "2025-01-15")
        line.profit_cost_category = "manual"
        self.assertEqual(line.profit_cost_category, "manual")
