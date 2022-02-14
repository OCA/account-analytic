# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def _onchange_product_id_analytic_default(self):
        rec = self.env["account.analytic.default"].account_get(
            product_id=self.product_id.id,
            partner_id=self.order_id.partner_id.id,
            user_id=self.env.uid,
            date=fields.Date.today(),
            company_id=self.order_id.company_id.id,
        )
        if rec:
            if rec.analytic_id:
                self.account_analytic_id = rec.analytic_id.id
            if rec.analytic_tag_ids:
                self.analytic_tag_ids = rec.analytic_tag_ids
        else:
            self.account_analytic_id = False
            self.analytic_tag_ids = False
