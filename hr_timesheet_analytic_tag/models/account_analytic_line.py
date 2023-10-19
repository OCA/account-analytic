# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import Command, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_preprocess(self, vals):
        res = super()._timesheet_preprocess(vals)
        if vals.get("task_id") and not vals.get("tag_ids"):
            task = self.env["project.task"].browse(vals.get("task_id"))
            vals.update(tag_ids=[Command.set(task.analytic_tag_ids.ids)])
        return res
