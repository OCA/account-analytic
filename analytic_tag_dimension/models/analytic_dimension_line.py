# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AnalyticDimensionLine(models.AbstractModel):
    _name = 'analytic.dimension.line'
    _description = 'Analytic Dimension Line'
    _analytic_tag_field_name = 'analytic_tag_ids'

    @api.multi
    def _handle_analytic_dimension(self):
        for adl in self:
            tag_ids = adl[self._analytic_tag_field_name]
            tag_ids._check_analytic_dimension()
            dimension_values = tag_ids.get_dimension_values()
            super(AnalyticDimensionLine, adl).write(dimension_values)

    @api.model
    def create(self, values):
        result = super(AnalyticDimensionLine, self).create(values)
        if values.get(result._analytic_tag_field_name):
            result._handle_analytic_dimension()
        return result

    @api.multi
    def write(self, values):
        result = super(AnalyticDimensionLine, self).write(values)
        if values.get(self._analytic_tag_field_name):
            self._handle_analytic_dimension()
        return result
