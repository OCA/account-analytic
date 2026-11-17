from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    tag_ids = fields.Many2many(
        "account.analytic.tag",
        "account_analytic_line_tag_rel",
        "line_id",
        "tag_id",
        string="Tags",
    )
