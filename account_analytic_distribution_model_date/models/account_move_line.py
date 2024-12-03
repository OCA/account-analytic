# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import frozendict


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line"]

    @api.depends("account_id", "partner_id", "product_id")
    def _compute_analytic_distribution(self):
        cache = {}
        for line in self:
            if line.display_type == "product" or not line.move_id.is_invoice(
                include_receipts=True
            ):
                arguments = frozendict(
                    {
                        "product_id": line.product_id.id,
                        "product_categ_id": line.product_id.categ_id.id,
                        "partner_id": line.partner_id.id,
                        "partner_category_id": line.partner_id.category_id.ids,
                        "account_prefix": line.account_id.code,
                        "company_id": line.company_id.id,
                        "date": self._get_date(line).strftime("%Y-%m-%d"),
                    }
                )
                if arguments not in cache:
                    cache[arguments] = self.env[
                        "account.analytic.distribution.model"
                    ]._get_distribution(arguments)
                line.analytic_distribution = (
                    cache[arguments] or line.analytic_distribution
                )

    def _get_date(self, line):
        return line.invoice_date or fields.Date.today()
