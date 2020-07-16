# Copyright 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _compute_num_productions(self):
        production = self.env["mrp.production"]
        for analytic_account in self:
            domain = [("analytic_account_id", "=", analytic_account.id)]
            analytic_account.num_productions = production.search_count(domain)

    num_productions = fields.Integer(compute="_compute_num_productions")
