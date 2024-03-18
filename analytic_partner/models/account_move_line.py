# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_line(self):
        values_list = super(AccountMoveLine, self)._prepare_analytic_line()
        for index, move_line in enumerate(self):
            values = values_list[index]
            values[
                "other_partner_id"
            ] = move_line.move_id.partner_id.commercial_partner_id.id
        return values_list
