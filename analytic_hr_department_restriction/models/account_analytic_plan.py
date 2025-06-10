# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import config


class AccountAnalyticPlan(models.Model):
    _inherit = "account.analytic.plan"

    department_ids = fields.Many2many(
        comodel_name="hr.department",
        string="Departments",
    )

    def _get_all_plans(self):
        """We need to do the search again to avoid possible access errors.
        This is because the __get_all_plans() method gets all plans with .sudo() and
        therefore does not filter properly."""
        project_plan, other_plans = super()._get_all_plans()
        test_condition = not config["test_enable"] or self.env.context.get(
            "test_analytic_hr_department_restriction"
        )
        if test_condition:
            project_plan = self.search([("id", "in", project_plan.ids)])
            other_plans = self.search([("id", "in", other_plans.ids)])
        return project_plan, other_plans
