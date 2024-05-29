from odoo import fields, models


class AccountAnalyticCategory(models.Model):
    _name = "account.analytic.category"
    _description = "Analytic Categories"
    _order = "sequence,id"

    name = fields.Char(required=True)
    sequence = fields.Integer()
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
