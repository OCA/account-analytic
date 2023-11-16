# Copyright 2017 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _compute_analytic_distribution(self):
        """
        Get analytic distribution from product expense analytic account
        If no account is set, call super with those records
        """
        lines_without_analytic_ids = set()
        for line in self:
            if line.product_id:
                ana_accounts = (
                    line.product_id.product_tmpl_id._get_product_analytic_accounts()
                )
                ana_account = ana_accounts["expense"]
                if ana_account:
                    line.analytic_distribution = {ana_account.id: 100}
                else:
                    lines_without_analytic_ids.add(line.id)
        return super(
            PurchaseOrderLine, self.browse(lines_without_analytic_ids)
        )._compute_analytic_distribution()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("product_id") and not vals.get("analytic_distribution"):
                product = self.env["product.product"].browse(vals.get("product_id"))
                ana_accounts = product.product_tmpl_id._get_product_analytic_accounts()
                ana_account = ana_accounts["expense"]
                vals["analytic_distribution"] = (
                    {ana_account.id: 100.0} if ana_account else False
                )
        return super().create(vals_list)
