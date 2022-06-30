# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):

    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        """
        If the grouping strategy is set 'per order' and if an analytic
        account is set on procurement, add the analytic account in the
        criteria to find an eligible purchase order.
        """
        domain = super()._make_po_get_domain(company_id, values, partner)
        if company_id.purchase_analytic_grouping == "order":
            analytic_id = values.get("analytic_account_id")
            if analytic_id:
                domain += (("order_line.account_analytic_id", "=", analytic_id),)
        return domain
