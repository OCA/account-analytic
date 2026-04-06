# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    department_ids = fields.Many2many(
        comodel_name="hr.department",
        string="Departments",
        domain="['|',('company_id', '=?', company_id),('company_id', '=', False)]",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            user = self.env.user
            user.invalidate_recordset(["employee_ids"])
            user = user.with_context(allowed_company_ids=user.company_ids.ids)
            departments = user.employee_ids.department_id
            if departments:
                for vals in vals_list:
                    if not vals.get("department_ids"):
                        vals["department_ids"] = [Command.set(departments.ids)]
        return super().create(vals_list)
