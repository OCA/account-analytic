# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Any

from odoo import api, models


class AccountAnalyticPlan(models.Model):
    _inherit = "account.analytic.plan"

    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> Any:
        plans = super().create(vals_list)
        self.env["account.analytic.line"]._clear_analytic_plan_cache()
        return plans

    def write(self, vals: dict[str, Any]) -> bool:
        result = super().write(vals)
        if result:
            self.env["account.analytic.line"]._clear_analytic_plan_cache()
        return result

    def unlink(self) -> bool:
        result = super().unlink()
        if result:
            self.env["account.analytic.line"]._clear_analytic_plan_cache()
        return result
