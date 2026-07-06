# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.constrains("plan_id", "parent_id")
    def _check_parent_plan(self):
        for acc in self:
            if acc.parent_id and acc.parent_id.plan_id != acc.plan_id:
                raise ValidationError(
                    _(
                        "The analytic account '%(child)s' must belong to the "
                        "same analytic plan as its parent '%(parent)s'.",
                        child=acc.display_name,
                        parent=acc.parent_id.display_name,
                    )
                )
            mismatched = acc.child_ids.filtered(
                lambda c, acc=acc: c.plan_id != acc.plan_id
            )
            if mismatched:
                raise ValidationError(
                    _(
                        "The analytic account '%(parent)s' must belong to the "
                        "same analytic plan as its children: %(children)s.",
                        parent=acc.display_name,
                        children=", ".join(mismatched.mapped("display_name")),
                    )
                )
