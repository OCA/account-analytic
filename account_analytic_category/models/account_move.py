from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        moves._set_line_analytic_category_ids()
        return moves

    def write(self, values):
        super().write(values)
        self._set_line_analytic_category_ids()
        return True

    def _set_line_analytic_category_ids(self):
        for move in self:
            move.line_ids._set_analytic_category_ids()
