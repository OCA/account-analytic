# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        account_analytic_id = self.account_analytic_id
        res = super()._onchange_product_id()
        if not self.env.context.get('pos_analytic') or not account_analytic_id:
            return res
        # Odoo triggers an onchange on the product_id when creating an invoice.
        # This may cause an incompatibility with product_analytic
        if self.account_analytic_id != account_analytic_id:
            self.account_analytic_id = account_analytic_id
        return res
