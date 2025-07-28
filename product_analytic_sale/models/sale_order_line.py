# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    analytic_distribution = fields.Many2one(
        "account.analytic.distribution",
        compute="_compute_analytic_distribution",
        readonly=True,
        help="Distribució analítica per defecte definida al producte o categoria",
    )

    @api.depends("product_id")
    def _compute_analytic_distribution(self):
        """
        Manual calculation of the analytic distribution:
        1) Get the income account of the product (if it exists)
        2) Assign 100% of the line to that account
        3) If there is no account, leave the distribution empty
        """
        for line in self:
            # without product there is no distribution
            if not line.product_id:
                line.analytic_distribution = {}
                continue

            # product_analytic defines this method to return
            # {'income': analytic_account, 'expense': analytic_account}
            accounts = line.product_id.product_tmpl_id._get_product_analytic_accounts()
            income_ana = accounts.get("income")

            if income_ana:
                # total income account
                line.analytic_distribution = {income_ana.id: 100}
            else:
                # no default distribution
                line.analytic_distribution = {}
