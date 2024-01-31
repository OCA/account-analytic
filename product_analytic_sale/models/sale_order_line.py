# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_analytic_distribution(self):
        """
        Get analytic distribution from product expense analytic account
        If no account is set, call super with those records
        """
        lines_without_analytic_ids = self.browse()
        for line in self:
            if line.product_id:
                ana_accounts = (
                    line.product_id.product_tmpl_id._get_product_analytic_accounts()
                )
                ana_account = ana_accounts["income"]
                if ana_account:
                    line.analytic_distribution = {ana_account.id: 100}
                    continue
            lines_without_analytic_ids |= line
        return super(
            SaleOrderLine, lines_without_analytic_ids
        )._compute_analytic_distribution()
