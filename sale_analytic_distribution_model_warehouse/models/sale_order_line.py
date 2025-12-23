# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.partner_id", "product_id")
    def _compute_analytic_distribution(self):
        for line in self:
            line = line.with_context(warehouse_id=line.order_id.warehouse_id.id)
            super(SaleOrderLine, line)._compute_analytic_distribution()
        return
