# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        if self.product_id:
            ana_account = (
                self.product_id.product_tmpl_id._get_product_analytic_accounts()[
                    "income"
                ]
            )
            if ana_account:
                vals["analytic_account_id"] = ana_account.id
        return vals
