# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

INV_TYPE_MAP = {
    "out_invoice": "income",
    "out_refund": "income",
    "out_receipt": "income",
    "in_invoice": "expense",
    "in_refund": "expense",
    "in_receipt": "expense",
}


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    @api.model
    def _get_distribution(self, vals):
        res = super()._get_distribution(vals)
        if res:
            return res
        # Compatibility with `pos_analytic_by_config`
        if self.env.context.get("pos_config_id"):
            return res
        # Compute distribution from product
        move_type = self.env.context.get("move_type")
        if vals.get("product_id") and move_type and move_type in INV_TYPE_MAP:
            product = self.env["product.product"].browse(vals["product_id"])
            ana_accounts = product.product_tmpl_id._get_product_analytic_accounts()
            ana_account = ana_accounts[INV_TYPE_MAP[move_type]]
            if ana_account:
                return {ana_account.id: 100}
        return res
