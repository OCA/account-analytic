from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "analytic.mixin"]

    @api.depends("analytic_distribution")
    def _compute_analytic_account_ids(self):
        return super()._compute_analytic_account_ids()

    analytic_account_ids = fields.Many2many(
        store=True,
        compute="_compute_analytic_account_ids",
    )
