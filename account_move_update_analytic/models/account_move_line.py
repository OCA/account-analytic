# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

force_state_sentinel = object()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_reconciliation(self):
        """
        Pass the check if we're asked to
        """
        if self.env.context.get("account_move_update_analytic") == force_state_sentinel:
            return
        return super()._check_reconciliation()

    def _compute_all_tax(self):
        """
        super() doesn't write the analytic distribution when the move is posted.
        For our purposes, we need that, so we manipulate the cache for the move to
        look like it is in draft state when we're called by the update wizard
        """

        cache = self.env.cache._data[self.move_id._fields["state"]]

        if self.env.context.get("account_move_update_analytic") == force_state_sentinel:
            cache[self.move_id.id] = "draft"

        result = super()._compute_all_tax()

        if self.env.context.get("account_move_update_analytic") == force_state_sentinel:
            if self.move_id.id in cache:
                del cache[self.move_id.id]

        return result
