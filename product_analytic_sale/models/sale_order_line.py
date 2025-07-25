# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    analytic_distribution = fields.Text(
        readonly=True,
        compute="_compute_analytic_distribution",
        help="Distribution for analytic entries, as {account_id: percent}",
    )

    @api.depends("product_id")
    def _compute_analytic_distribution(self):
        for line in self:
            if line.product_id:
                accounts = (
                    line.product_id.product_tmpl_id._get_product_analytic_accounts()
                )
                income_ana = accounts.get("income")
                if income_ana:
                    line.analytic_distribution = json.dumps({income_ana.id: 100.0})
                    continue
            line.analytic_distribution = json.dumps({})
