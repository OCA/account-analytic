# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_analytic_distribution(self):
        for line in self:
            move_type = self.env.context.get("move_type", line.move_id.move_type)
            super(
                AccountMoveLine, line.with_context(move_type=move_type)
            )._compute_analytic_distribution()
        return
