# Copyright 2023-2026 Tecnativa - Víctor Martínez
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

    def _prepare_payments_vals(self):
        move_vals, payment_vals = super()._prepare_payments_vals()
        if self.analytic_tag_ids:
            for _, _, line_vals in move_vals["line_ids"]:
                if line_vals.get("expense_id") and line_vals["expense_id"] == self.id:
                    line_vals.update(
                        {"analytic_tag_ids": [Command.set(self.analytic_tag_ids.ids)]}
                    )
        return move_vals, payment_vals
