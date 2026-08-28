# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    manual_distribution_id = fields.Many2one("account.analytic.distribution.manual")

    @api.model
    def _select(self) -> SQL:
        return SQL("%s, line.manual_distribution_id", super()._select())
