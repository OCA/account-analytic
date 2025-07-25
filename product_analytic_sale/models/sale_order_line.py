# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    analytic_distribution_id = fields.Many2one(
        "account.analytic.distribution",
        compute="_compute_analytic_distribution",
        readonly=True,
        help="Distribució analítica per defecte definida al producte o categoria",
    )

    @api.depends("product_id")
    def _compute_analytic_distribution(self):
        for line in self:
            # Priority: product distribution, if not, category distribution
            dist = (
                line.product_id.analytic_distribution_id
                or line.product_id.categ_id.analytic_distribution_id
            )
            line.analytic_distribution_id = dist and dist.id or False

    @api.onchange("product_id")
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        # Assign analytic account if it exists
        analytic = self.product_id.analytic_account_id
        if analytic:
            self.analytic_account_id = analytic.id
        # Recompute analytic distribution
        self._compute_analytic_distribution()
        return res

    def _prepare_invoice_line(self):
        vals = super()._prepare_invoice_line()
        if self.product_id.analytic_account_id:
            vals["analytic_account_id"] = self.product_id.analytic_account_id.id
        if self.analytic_distribution_id:
            vals["analytic_distribution_id"] = self.analytic_distribution_id.id
        return vals
