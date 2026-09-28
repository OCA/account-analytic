# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.analytic_cost_distribution.tests.common import (
    CostDistributionCommon,
)


class TestIndirectCostDistributionModel(CostDistributionCommon):
    def test_allowed_plans_include_children(self):
        """Allowed plans must include the root and all its descendants."""
        allowed = self.model_timesheet.allowed_indirect_cost_plan_ids
        self.assertIn(self.plan_indirect_root, allowed)
        self.assertIn(self.plan_indirect_child, allowed)
        allowed_profit = self.model_timesheet.allowed_profit_centre_plan_ids
        self.assertIn(self.plan_profit_root, allowed_profit)
        self.assertIn(self.plan_profit_child, allowed_profit)

    def test_allowed_plans_populated_on_new_record(self):
        """The compute must fire on a new (unsaved) record too.

        Records reached from a NewId record are themselves NewId-wrapped,
        so compare against ``_origin`` to match real records.
        """
        new = self.DistributionModel.new(
            {"name": "Draft", "company_id": self.company.id}
        )
        self.assertIn(
            self.plan_indirect_root,
            new.allowed_indirect_cost_plan_ids._origin,
        )
        self.assertIn(
            self.plan_profit_root,
            new.allowed_profit_centre_plan_ids._origin,
        )

    def test_plans_outside_roots_are_rejected(self):
        """Picking a plan not under the configured company roots raises."""
        stray = self.AnalyticPlan.create({"name": "Stray plan"})
        with self.assertRaises(ValidationError):
            self.model_timesheet.indirect_cost_plan_ids = [(4, stray.id)]

    def test_get_indirect_cost_accounts(self):
        accounts = self.model_timesheet._get_indirect_cost_accounts()
        self.assertIn(self.indirect_account, accounts)
        self.assertNotIn(self.profit_account_a, accounts)

    def test_get_profit_centre_accounts(self):
        accounts = self.model_timesheet._get_profit_centre_accounts()
        self.assertIn(self.profit_account_a, accounts)
        self.assertIn(self.profit_account_b, accounts)
        self.assertNotIn(self.indirect_account, accounts)

    def test_plan_with_children_recursive(self):
        """A nested grandchild plan must be returned too."""
        grandchild = self.AnalyticPlan.create(
            {"name": "Indirect grandchild", "parent_id": self.plan_indirect_child.id}
        )
        plans = self.model_timesheet._get_plan_with_children(self.plan_indirect_root)
        self.assertIn(grandchild, plans)
