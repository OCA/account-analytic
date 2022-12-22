# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, models

INV_TYPE_MAP = {
    "out_invoice": "income",
    "out_refund": "income",
    "out_receipt": "income",
    "in_invoice": "expense",
    "in_refund": "expense",
    "in_receipt": "expense",
}


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        for line in self:
            inv_type = line.move_id.move_type
            if line.product_id and self._has_invoice_type(inv_type):
                ana_accounts = (
                    line.product_id.product_tmpl_id._get_product_analytic_accounts()
                )
                ana_account = ana_accounts[INV_TYPE_MAP[inv_type]]
                line.analytic_account_id = ana_account.id
                dict_tags = line.product_id.product_tmpl_id._get_product_analytic_tags()
                analytic_tags = dict_tags[INV_TYPE_MAP[inv_type]]
                line.analytic_tag_ids = analytic_tags
        return res

    def _has_invoice_type(self, inv_type):
        return inv_type in [
            "out_invoice",
            "out_refund",
            "out_receipt",
            "in_invoice",
            "in_refund",
            "in_receipt",
        ]

    def _apply_product_analytic_accounts(self, vals, inv_type):
        return (
            vals.get("product_id")
            and self._has_invoice_type(inv_type)
            and not vals.get("analytic_account_id")
        )

    def _apply_product_analytic_tags(self, vals, inv_type):
        tags_value = vals.get("analytic_tag_ids")
        empty_tags = not tags_value or (
            isinstance(tags_value, list) and tags_value == [(6, 0, [])]
        )
        return (
            vals.get("product_id") and self._has_invoice_type(inv_type) and empty_tags
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            inv_type = self.env["account.move"].browse([vals.get("move_id")]).move_type
            if self._apply_product_analytic_accounts(vals, inv_type):
                product = self.env["product.product"].browse(vals.get("product_id"))
                ana_accounts = product.product_tmpl_id._get_product_analytic_accounts()
                ana_account = ana_accounts[INV_TYPE_MAP[inv_type]]
                if ana_account:
                    vals["analytic_account_id"] = ana_account.id
            if self._apply_product_analytic_tags(vals, inv_type):
                product = self.env["product.product"].browse(vals.get("product_id"))
                dict_tags = product.product_tmpl_id.sudo(
                    False
                )._get_product_analytic_tags()
                analytic_tags = dict_tags[INV_TYPE_MAP[inv_type]]
                if analytic_tags:
                    vals["analytic_tag_ids"] = [Command.set(analytic_tags.ids)]
        return super().create(vals_list)
