# Copyright 2026 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class BlanketOrderWizard(models.TransientModel):
    _inherit = "purchase.blanket.order.wizard"

    def create_purchase_order(self):
        action = super().create_purchase_order()
        po_ids = action["domain"][0][2]
        po_lines = self.env["purchase.order.line"].search(
            [("order_id", "in", po_ids), ("blanket_order_line", "!=", False)]
        )
        for po_line in po_lines:
            distribution = po_line.blanket_order_line.analytic_distribution
            if distribution:
                po_line.analytic_distribution = distribution
        return action
