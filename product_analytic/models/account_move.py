# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
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
        for line in self:
            inv_type = line.move_id.move_type
            if line.product_id and inv_type:
                ana_accounts = (
                    line.product_id.product_tmpl_id._get_product_analytic_accounts()
                )
                ana_account = ana_accounts[INV_TYPE_MAP[inv_type]]
                line.analytic_account_id = ana_account.id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            inv_type = self.env["account.move"].browse([vals.get("move_id")]).move_type
            if (
                vals.get("product_id")
                and inv_type != "entry"
                and not vals.get("analytic_account_id")
            ):
                product = self.env["product.product"].browse(vals.get("product_id"))
                ana_accounts = product.product_tmpl_id._get_product_analytic_accounts()
                ana_account = ana_accounts[INV_TYPE_MAP[inv_type]]
                vals["analytic_account_id"] = ana_account.id
        return super().create(vals_list)
