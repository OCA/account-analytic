# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    parent_analytic_item = fields.Many2one(
        "account.analytic.line", "Parent Analytic Item", ondelete="cascade"
    )

    @api.model
    def create(self, vals):
        cost_rule_obj = self.env["activity.cost.rule"]
        res = super(AccountAnalyticLine, self).create(vals)
        if vals.get("project_id"):
            cost_rules = cost_rule_obj.search(
                [("project_id", "=", vals.get("project_id"))]
            )
            for rule in cost_rules:
                rule_vals = {
                    "name": res.name,
                    "product_id": rule.cost_type_product_id.id,
                    "unit_amount": res.unit_amount * rule.factor,
                    "parent_analytic_item": res.id,
                    "account_id": rule.project_id.analytic_account_id.id,
                    "date": rule.date_start or datetime.today(),
                }
                analytic_line = self.create(rule_vals)
                analytic_line.on_change_unit_amount()
        return res

    def write(self, vals):
        if vals.get("unit_amount"):
            child_analytic_lines = self.search(
                [
                    ("project_id", "=", vals.get("project_id")),
                    ("parent_analytic_item", "=", self.id),
                ]
            )
            for line in child_analytic_lines:
                line.unit_amount = vals.get("unit_amount")
                line.on_change_unit_amount()
        res = super(AccountAnalyticLine, self).write(vals)
        return res
