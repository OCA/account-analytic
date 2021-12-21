# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        analytic_account_id = self.analytic_account_id
        res = super()._onchange_product_id()
        if not self.env.context.get("pos_analytic") or not analytic_account_id:
            return res
        # Odoo triggers an onchange on the product_id when creating an invoice.
        # This may cause an incompatibility with product_analytic
        if self.analytic_account_id != analytic_account_id:
            self.analytic_account_id = analytic_account_id
        return res
