from odoo import api, models

from odoo.addons.product_analytic.models.account_analytic_distribution_model import (
    INV_TYPE_MAP,
)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("account_id", "partner_id", "product_id")
    def _compute_analytic_distribution(self):
        res = super()._compute_analytic_distribution()
        lines_without_analytic = self.filtered(
            lambda line: not line.analytic_distribution
            and line.product_id
            and line.move_id
        )
        for line in lines_without_analytic:
            if line.display_type or not line.product_id:
                continue
            ana_accounts = (
                line.product_id.product_tmpl_id._get_product_analytic_accounts()
            )
            invoice_type = line.move_id.move_type
            if invoice_type not in INV_TYPE_MAP:
                continue
            ana_account = ana_accounts[INV_TYPE_MAP[invoice_type]]
            if ana_account:
                line.analytic_distribution = ana_account
                continue
            lines_without_analytic |= line
        return res
