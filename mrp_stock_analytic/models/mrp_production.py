# Copyright 2021 ACSONE SA/NV
# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "analytic.mixin"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
        states={
            "done": [("readonly", True)],
            "cancel": [("readonly", True)],
        },
    )

    def _inverse_analytic_distribution(self):
        """If analytic distribution is set on production, write it on all component
        moves.
        """
        for production in self:
            production.move_raw_ids.write(
                {"analytic_distribution": production.analytic_distribution}
            )

    def button_mark_done(self):
        self = self.with_context(validate_analytic=True)
        return super().button_mark_done()
