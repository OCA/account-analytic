from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_analytic_tags = fields.Boolean(
        string="Analytic Tags", implied_group="account_analytic_tag.group_analytic_tags"
    )
