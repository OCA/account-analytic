from odoo import api, models


class AccountAnalyticDimension(models.Model):
    _inherit = "account.analytic.dimension"

    @api.model
    def get_model_names(self):
        return super().get_model_names() + ["sale.order.line"]
