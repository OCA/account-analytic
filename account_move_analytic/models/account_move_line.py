# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id.analytic_distribution")
    def _compute_analytic_distribution(self):
        return super()._compute_analytic_distribution()

    def _related_analytic_distribution(self):
        vals = super()._related_analytic_distribution()
        if self.move_id.analytic_distribution and not self.analytic_distribution:
            vals |= self.move_id.analytic_distribution or {}
        return vals
