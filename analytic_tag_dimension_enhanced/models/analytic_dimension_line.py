# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AnalyticDimensionLine(models.AbstractModel):
    _inherit = "analytic.dimension.line"

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            rec[self._analytic_tag_field_name]._check_required_dimension(rec)
        return res

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec[self._analytic_tag_field_name]._check_required_dimension(rec)
        return res
