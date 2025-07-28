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
        dist_model = self.env["account.analytic.distribution"]
        tag = self.env["account.analytic.tag"].search([], limit=1)
        for line in self:
            # Without product_id, no analytic distribution
            if not line.product_id:
                line.analytic_distribution = False
                continue

            # Get only the 'income' account from the product
            accounts = line.product_id.product_tmpl_id._get_product_analytic_accounts()
            income_ana = accounts.get("income")

            if not income_ana:
                line.analytic_distribution = False
                continue

            dist = dist_model.search(
                [
                    ("account_id", "=", income_ana.id),
                    ("percentage", "=", 100),
                    ("tag_id", "=", tag.id),
                ],
                limit=1,
            )

            if not dist:
                dist = dist_model.create(
                    {
                        "name": income_ana.name,
                        "account_id": income_ana.id,
                        "percentage": 100,
                        "tag_id": tag.id,
                    }
                )

            line.analytic_distribution = dist
