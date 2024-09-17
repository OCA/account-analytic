# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInvoiceOnshipping(models.TransientModel):

    _inherit = "stock.invoice.onshipping"

    def _get_invoice_line_values(self, moves, invoice_values, invoice):
        """
        Include the analytic account filled in picking when creating an invoice
        """
        values = super(StockInvoiceOnshipping, self)._get_invoice_line_values(
            moves, invoice_values, invoice
        )
        move = fields.first(moves)
        if move.analytic_account_id:
            values["analytic_account_id"] = move.analytic_account_id
        return values
