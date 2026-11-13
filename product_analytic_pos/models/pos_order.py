# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def _get_product_analytic_distribution(self, account):
        self.ensure_one()
        commercial_partner = self.order_id.partner_id.commercial_partner_id
        return self.env["account.analytic.distribution.model"]._get_distribution(
            {
                "product_id": self.product_id.id,
                "product_categ_id": self.product_id.categ_id.id,
                "partner_id": commercial_partner.id,
                "partner_category_id": commercial_partner.category_id.ids,
                "account_prefix": account.code,
                "company_id": self.company_id.id,
            }
        )

    def _prepare_base_line_for_taxes_computation(self):
        base_line = super()._prepare_base_line_for_taxes_computation()
        if not base_line.get("analytic_distribution"):
            base_line["analytic_distribution"] = (
                self._get_product_analytic_distribution(base_line["account_id"])
            )
        return base_line
