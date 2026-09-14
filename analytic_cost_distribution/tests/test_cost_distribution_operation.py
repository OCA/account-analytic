# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.analytic_cost_distribution.tests.common import (
    CostDistributionCommon,
)


@tagged("post_install", "-at_install")
class TestCostDistributionOperation(CostDistributionCommon):
    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create(
            {
                "name": "Test project",
                "allow_timesheets": True,
                "account_id": self.profit_account_a.id,
            }
        )

    def _new_operation(self, date_from="2025-01-01", date_to="2025-01-31"):
        return self.Operation.create(
            {
                "date_from": date_from,
                "date_to": date_to,
                "distribution_date": date_to,
            }
        )

    def test_sequence_assigned_on_create(self):
        operation = self._new_operation()
        self.assertNotEqual(operation.name, "/")
        self.assertTrue(operation.name.startswith("ICDO/"))

    def test_compute_raises_without_models(self):
        self.model_timesheet.active = False
        operation = self._new_operation()
        with self.assertRaises(UserError):
            operation.action_compute()

    def test_compute_raises_on_conflicting_models(self):
        # Second model also covers plan_indirect_child → conflict
        self.DistributionModel.create(
            {
                "name": "Conflicting model",
                "indirect_cost_plan_ids": [(6, 0, self.plan_indirect_child.ids)],
                "profit_centre_plan_ids": [(6, 0, self.plan_profit_child.ids)],
            }
        )
        operation = self._new_operation()
        with self.assertRaises(UserError):
            operation.action_compute()

    def test_compute_raises_on_uncovered_account(self):
        # Account directly under the indirect-cost ROOT plan
        # (which is not covered by any model)
        uncovered = self.AnalyticAccount.create(
            {"name": "Uncovered", "plan_id": self.plan_indirect_root.id}
        )
        self._create_cost_line(uncovered, 100, "2025-01-10")
        operation = self._new_operation()
        with self.assertRaises(UserError):
            operation.action_compute()

    def test_compute_groups_lines_by_model(self):
        self._create_cost_line(self.indirect_account, 100, "2025-01-10")
        self._create_cost_line(self.indirect_account, 200, "2025-01-20")
        # Cost line outside the period must be ignored
        self._create_cost_line(self.indirect_account, 999, "2024-12-15")
        # Profit line in period must be ignored (positive amount)
        self._create_profit_line(self.profit_account_a, 500, "2025-01-10")

        operation = self._new_operation()
        operation.action_compute()
        self.assertEqual(len(operation.line_ids), 1)
        op_line = operation.line_ids
        self.assertEqual(op_line.distribution_model_id, self.model_timesheet)
        self.assertEqual(op_line.source_amount, -300.0)
        self.assertEqual(len(op_line.source_line_ids), 2)

    def test_distribute_timesheet_method(self):
        self._create_cost_line(self.indirect_account, 1000, "2025-01-15")
        self._create_timesheet_line(
            self.profit_account_a, 40.0, "2025-01-10", self.project
        )
        # Profit-centre B gets 60 hours via a non-project line is *not*
        # counted as a timesheet — for B we also need project_id set.
        project_b = self.env["project.project"].create(
            {
                "name": "Project B",
                "allow_timesheets": True,
                "account_id": self.profit_account_b.id,
            }
        )
        self._create_timesheet_line(
            self.profit_account_b, 60.0, "2025-01-12", project_b
        )

        operation = self._new_operation()
        operation.action_compute()
        operation.action_distribute()

        self.assertEqual(operation.state, "done")
        distributed = operation.distributed_line_ids
        self.assertEqual(len(distributed), 2)

        amounts = {line.account_id: line.amount for line in distributed}
        # 40% to A, 60% to B, both negative (costs)
        self.assertAlmostEqual(amounts[self.profit_account_a], -400.0)
        self.assertAlmostEqual(amounts[self.profit_account_b], -600.0)

    def test_distribute_profits_method(self):
        self.model_timesheet.distribution_method = "profits"
        source = self._create_cost_line(self.indirect_account, 1000, "2025-01-15")
        # Profits in profit centres (positive amounts)
        self._create_profit_line(self.profit_account_a, 2500, "2025-01-10")
        self._create_profit_line(self.profit_account_b, 7500, "2025-01-12")

        operation = self._new_operation()
        operation.action_compute()
        operation.action_distribute()

        amounts = {
            line.account_id: line.amount for line in operation.distributed_line_ids
        }
        self.assertAlmostEqual(amounts[self.profit_account_a], -250.0)
        self.assertAlmostEqual(amounts[self.profit_account_b], -750.0)
        self.assertEqual(source.distributed_by_operation_id, operation)

        action = operation.action_view_distributed_lines()
        self.assertEqual(action["res_model"], "account.analytic.line")
        self.assertEqual(
            action["domain"],
            [("indirect_cost_distribution_operation_id", "=", operation.id)],
        )

        operation.action_reset_to_draft()
        self.assertEqual(operation.state, "draft")
        self.assertFalse(operation.distributed_line_ids)
        self.assertFalse(source.distributed_by_operation_id)

    def test_distribute_requires_compute(self):
        operation = self._new_operation()
        with self.assertRaises(UserError):
            operation.action_distribute()

    def test_compute_excludes_already_distributed(self):
        """Re-running a fresh compute on a period whose costs were already
        distributed by a prior operation excludes those lines and returns a
        warning notification."""
        self._create_cost_line(self.indirect_account, 100, "2025-01-10")
        self._create_timesheet_line(
            self.profit_account_a, 5.0, "2025-01-10", self.project
        )
        op1 = self._new_operation()
        op1.action_compute()
        op1.action_distribute()

        op2 = self._new_operation()
        result = op2.action_compute()

        self.assertFalse(op2.line_ids)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("tag"), "display_notification")
