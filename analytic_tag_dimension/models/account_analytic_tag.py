# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    analytic_dimension_id = fields.Many2one(
        comodel_name='account.analytic.dimension',
        string='Dimension')

    @api.multi
    def get_dimension_values(self):
        values = {}
        for tag in self.filtered('analytic_dimension_id'):
            values.update({
                tag.analytic_dimension_id.get_field_name(): tag.id,
            })
        return values

    def _check_analytic_dimension(self):
        tags_with_dimension = self.filtered('analytic_dimension_id')
        dimensions = tags_with_dimension.mapped('analytic_dimension_id')
        if len(tags_with_dimension) != len(dimensions):
            raise ValidationError(
                _("You can not set two tags from same dimension."))

    def write(self, vals):
        if 'analytic_dimension_id' in vals:
            Dimension = self.env['account.analytic.dimension']
            _models = [self.env[m] for m in Dimension.get_model_names()]
            for tag in self.filtered('analytic_dimension_id'):
                old_field = tag.analytic_dimension_id.get_field_name()
                new_field = Dimension.browse(
                    vals['analytic_dimension_id']).get_field_name()
                if old_field == new_field:  # pragma: no cover
                    continue
                # Filter to avoid update report models
                for model in filter(lambda m: m._auto, _models):
                    records_to_update = model.search([
                        (old_field, '=', tag.id),
                    ], order='id')
                    if not records_to_update:
                        continue
                    same_dimension_tags = records_to_update.with_context(
                        prefetch_fields=False).mapped(new_field)
                    if same_dimension_tags:
                        raise ValidationError(_(
                            "You can not set two tags from same dimension.\n"
                            " Records {} in the model {} have {}".format(
                                records_to_update.ids, model._description,
                                same_dimension_tags.mapped('display_name'))
                        ))
                    records_to_update.write({
                        old_field: False,
                        new_field: tag.id,
                    })
        return super().write(vals)
