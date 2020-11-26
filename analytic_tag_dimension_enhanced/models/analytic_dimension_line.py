# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AnalyticDimensionLine(models.AbstractModel):
    _inherit = "analytic.dimension.line"

    def create(self, vals):
        rec = super().create(vals)
        rec[self._analytic_tag_field_name]._check_required_dimension(rec)
        return rec

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec[self._analytic_tag_field_name]._check_required_dimension(rec)
        return res
