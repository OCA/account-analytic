# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        check_company=True,
    )

    def _prepare_move_lines_vals(self):
        vals = super()._prepare_move_lines_vals()
        if self.analytic_tag_ids:
            vals.update({"analytic_tag_ids": [Command.set(self.analytic_tag_ids.ids)]})
        return vals
