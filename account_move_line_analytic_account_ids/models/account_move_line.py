from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "analytic.mixin"]

    analytic_account_ids = fields.Many2many(store=True)
