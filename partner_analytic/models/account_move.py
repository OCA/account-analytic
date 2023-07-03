# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

INV_TYPE_MAP = {
    "out_invoice": "income",
    "out_refund": "income",
    "in_invoice": "expense",
    "in_refund": "expense",
}


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        inv_type = self.move_id.move_type
        partner = self.move_id.partner_id
        if (
            partner
            and inv_type
            and inv_type in INV_TYPE_MAP
            and not self.analytic_account_id
        ):
            an_accs = partner.get_partner_analytic_accounts()
            an_acc = an_accs[INV_TYPE_MAP[inv_type]]
            self.analytic_account_id = an_acc
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "move_id" not in vals:
                continue
            move = self.env["account.move"].browse(vals.get("move_id"))
            partner = move.partner_id
            inv_type = move.move_type
            company_id = move.company_id.id if move.company_id else False
            if (
                partner
                and inv_type
                and inv_type in INV_TYPE_MAP
                and not vals.get("analytic_account_id", False)
            ):
                an_accs = partner.get_partner_analytic_accounts(company_id)
                an_acc = an_accs[INV_TYPE_MAP[inv_type]]
                vals.update({"analytic_account_id": an_acc.id})
        return super().create(vals_list)
