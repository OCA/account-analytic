# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        vals = super()._prepare_invoice_values(order, name, amount, so_line)
        ana_account = self.product_id.product_tmpl_id._get_product_analytic_accounts()[
            "income"
        ]
        if ana_account:
            vals["invoice_line_ids"][0][2]["analytic_account_id"] = ana_account.id
        return vals
