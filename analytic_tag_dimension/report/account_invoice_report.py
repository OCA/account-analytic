# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    def _get_dimension_fields(self):
        if self.env.context.get("update_custom_fields"):
            return []  # Avoid to report these columns when not yet created
        return [
            x
            for x in self.env["account.move.line"].fields_get().keys()
            if x.startswith("x_dimension_")
        ]

    @api.model
    def _select(self) -> SQL:
        dimension_fields = self._get_dimension_fields()
        dimension_fields_sql = [
            f", line.{field} as {field}" for field in dimension_fields
        ]
        return super()._select() + "".join(dimension_fields_sql)
