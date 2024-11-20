# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import Command, api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("task_id") and not vals.get("tag_ids"):
                task = self.env["project.task"].browse(vals.get("task_id"))
                vals["tag_ids"] = [Command.set(task.analytic_tag_ids.ids)]
        return super().create(vals_list)
