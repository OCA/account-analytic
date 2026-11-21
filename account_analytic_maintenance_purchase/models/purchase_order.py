from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_equipment_vals(self):
        vals = super()._prepare_equipment_vals()
        vals["analytic_distribution"] = self.analytic_distribution
        return vals
