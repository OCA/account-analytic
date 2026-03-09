# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("product_id", "order_id.partner_id")
    def _compute_analytic_distribution(self):
        for line in self:
            line = line.with_context(
                warehouse_id=line.order_id.picking_type_id.warehouse_id.id
            )
            super(PurchaseOrderLine, line)._compute_analytic_distribution()
        return
