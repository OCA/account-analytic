# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _compute_num_scraps(self):
        scrap = self.env["stock.scrap"]
        for analytic_account in self:
            domain = [("analytic_account_id", "=", analytic_account.id)]
            analytic_account.num_scraps = scrap.search_count(domain)

    num_scraps = fields.Integer(compute="_compute_num_scraps")
