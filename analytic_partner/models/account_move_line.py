# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_distribution_line(
        self, distribution, account_id, distribution_on_each_plan
    ):
        vals = super()._prepare_analytic_distribution_line(
            distribution, account_id, distribution_on_each_plan
        )
        vals["other_partner_id"] = self.move_id.partner_id.commercial_partner_id.id
        return vals
