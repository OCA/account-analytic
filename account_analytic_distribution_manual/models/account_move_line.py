# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_lines(self):
        vals = super()._prepare_analytic_lines()
        if self.manual_distribution_id:
            for val in vals:
                val.update({"manual_distribution_id": self.manual_distribution_id.id})
        return vals
