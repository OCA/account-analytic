from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        vals = super()._purchase_service_prepare_line_values(purchase_order, quantity)
        vals["analytic_distribution"] = self.analytic_distribution
        return vals
