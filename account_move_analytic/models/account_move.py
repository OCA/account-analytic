# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

INVOICE_TYPES = ("out_invoice", "out_refund", "in_invoice", "in_refund")


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "analytic.mixin"]

    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution")

    @api.depends("invoice_line_ids.analytic_distribution")
    def _compute_analytic_distribution(self):
        for move in self:
            if move.move_type not in INVOICE_TYPES:
                move.analytic_distribution = False
                continue
            product_lines = move.invoice_line_ids.filtered(
                lambda ln: ln.display_type not in ("line_section", "line_note")
            )
            if product_lines:
                first_distribution = product_lines[0].analytic_distribution or False
                for line in product_lines:
                    if line.analytic_distribution != first_distribution:
                        first_distribution = False
                        break
                move.analytic_distribution = first_distribution

    def _inverse_analytic_distribution(self):
        for move in self:
            if move.move_type not in INVOICE_TYPES:
                continue
            if move.analytic_distribution:
                product_lines = move.invoice_line_ids.filtered(
                    lambda ln: ln.display_type not in ("line_section", "line_note")
                )
                product_lines.write(
                    {"analytic_distribution": move.analytic_distribution}
                )
