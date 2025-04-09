# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    def _get_dimension_fields(self):
        return [
            x
            for x in self.env["account.move.line"]._fields
            if x.startswith("x_dimension_")
        ]

    @api.model
    def _select(self) -> SQL:
        dimension_fields = self._get_dimension_fields()
        dimension_fields = SQL(
            ", ".join(f"line.{field} as {field}" for field in dimension_fields)
        )
        return SQL("%s, %s", super()._select(), dimension_fields)
