from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("order_id")
    def _compute_analytic_distribution(self):
        super()._compute_analytic_distribution()
        maintenance_request_id = self.env.context.get("maintenance_request_id")
        if not maintenance_request_id:
            return
        request = self.env["maintenance.request"].browse(maintenance_request_id)
        distribution = request.equipment_id.analytic_distribution
        for line in self.filtered(lambda line: not line.analytic_distribution):
            line.analytic_distribution = distribution
