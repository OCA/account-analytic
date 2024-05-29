from odoo import fields, models


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    category_id = fields.Many2one(
        "account.analytic.category",
        string="Analytic Category",
    )
