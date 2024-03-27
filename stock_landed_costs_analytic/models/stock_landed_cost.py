from odoo import api, models


class StockLandedCost(models.Model):
    _name = "stock.landed.cost"
    _inherit = "stock.landed.cost"

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
