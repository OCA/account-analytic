# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    analytic_line_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        string="Analytic Lines",
        compute="_compute_analytic_line_ids",
    )

    @api.depends("line_ids.analytic_line_ids")
    def _compute_analytic_line_ids(self):
        for move in self:
            move.analytic_line_ids = move.line_ids.mapped("analytic_line_ids")
