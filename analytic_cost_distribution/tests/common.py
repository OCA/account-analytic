# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class CostDistributionCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AnalyticPlan = cls.env["account.analytic.plan"]
        cls.AnalyticAccount = cls.env["account.analytic.account"]
        cls.AnalyticLine = cls.env["account.analytic.line"]
        cls.DistributionModel = cls.env["indirect.cost.distribution.model"]
        cls.Operation = cls.env["indirect.cost.distribution.operation"]

        cls.company = cls.env.company

        # hr_timesheet refuses to create a timesheet line unless the current
        # user has an active employee in the company.
        if not cls.env["hr.employee"].search(
            [("user_id", "=", cls.env.user.id), ("company_id", "=", cls.company.id)],
            limit=1,
        ):
            cls.env["hr.employee"].create(
                {
                    "name": "Test Employee",
                    "user_id": cls.env.user.id,
                    "company_id": cls.company.id,
                }
            )

        # Indirect-cost plans: a root plan with one child plan
        cls.plan_indirect_root = cls.AnalyticPlan.create(
            {"name": "Indirect Costs Root"}
        )
        cls.plan_indirect_child = cls.AnalyticPlan.create(
            {"name": "Indirect Costs Child", "parent_id": cls.plan_indirect_root.id}
        )

        # Profit-centre plans: a root plan with one child plan
        cls.plan_profit_root = cls.AnalyticPlan.create({"name": "Profit Centres Root"})
        cls.plan_profit_child = cls.AnalyticPlan.create(
            {"name": "Profit Centres Child", "parent_id": cls.plan_profit_root.id}
        )

        # Configure the company
        cls.company.indirect_costs_root_plan_ids = [(6, 0, cls.plan_indirect_root.ids)]
        cls.company.profit_centres_root_plan_ids = [(6, 0, cls.plan_profit_root.ids)]

        # Accounts
        cls.indirect_account = cls.AnalyticAccount.create(
            {"name": "Rent", "plan_id": cls.plan_indirect_child.id}
        )
        cls.profit_account_a = cls.AnalyticAccount.create(
            {"name": "Profit Centre A", "plan_id": cls.plan_profit_child.id}
        )
        cls.profit_account_b = cls.AnalyticAccount.create(
            {"name": "Profit Centre B", "plan_id": cls.plan_profit_child.id}
        )

        # Distribution model covering the indirect-cost child plan and the
        # profit-centre child plan (timesheet method by default)
        cls.model_timesheet = cls.DistributionModel.create(
            {
                "name": "Timesheet model",
                "distribution_method": "timesheet",
                "indirect_cost_plan_ids": [(6, 0, cls.plan_indirect_child.ids)],
                "profit_centre_plan_ids": [(6, 0, cls.plan_profit_child.ids)],
            }
        )

    @classmethod
    def _create_cost_line(cls, account, amount, date, **extra):
        vals = {
            "name": "Cost line",
            "date": date,
            "account_id": account.id,
            "amount": -abs(amount),
            "company_id": cls.company.id,
        }
        vals.update(extra)
        return cls.AnalyticLine.create(vals)

    @classmethod
    def _create_profit_line(cls, account, amount, date, **extra):
        vals = {
            "name": "Profit line",
            "date": date,
            "account_id": account.id,
            "amount": abs(amount),
            "company_id": cls.company.id,
        }
        vals.update(extra)
        return cls.AnalyticLine.create(vals)

    @classmethod
    def _create_timesheet_line(cls, account, hours, date, project, **extra):
        vals = {
            "name": "Timesheet line",
            "date": date,
            "account_id": account.id,
            "unit_amount": hours,
            "company_id": cls.company.id,
            "project_id": project.id,
        }
        vals.update(extra)
        return cls.AnalyticLine.create(vals)
