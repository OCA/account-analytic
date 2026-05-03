# Copyright 2021 ACSONE SA/NV
# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "analytic.mixin"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
    )

    def _inverse_analytic_distribution(self):
        for rec in self:
            rec.move_raw_ids.write({"analytic_distribution": rec.analytic_distribution})
            if rec.company_id.mrp_analytic_on_finished:
                rec.move_finished_ids.write(
                    {"analytic_distribution": rec.analytic_distribution}
                )

    def _validate_analytic_distribution(self):
        for rec in self:
            rec._validate_distribution(
                product=rec.product_id.id,
                picking_type=rec.picking_type_id.id,
                business_domain="manufacturing_order",
                company_id=rec.company_id.id,
            )

    def button_mark_done(self):
        self = self.with_context(validate_analytic=True)
        self._validate_analytic_distribution()
        return super().button_mark_done()
