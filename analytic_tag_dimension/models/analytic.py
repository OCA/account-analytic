# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountAnalyticDimension(models.Model):
    _name = 'account.analytic.dimension'
    _description = 'Account Analytic Dimension'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    analytic_tag_ids = fields.One2many(
        comodel_name='account.analytic.tag',
        inverse_name='analytic_dimension_id',
        string='Analytic Tags')

    @api.constrains('code')
    def _check_code(self):
        for dimension in self:
            if ' ' in dimension.code:
                raise ValidationError(_("Code can't contain spaces!"))

    @api.model
    def get_model_names(self):
        return [
            'account.move.line',
            'account.analytic.line',
            'account.invoice.line',
            'account.invoice.report',
        ]

    def get_field_name(self, code=False):
        return 'x_dimension_{}'.format(code or self.code).lower()

    @api.model
    def create(self, values):
        res = super().create(values)
        _models = self.env['ir.model'].search([
            ('model', 'in', self.get_model_names()),
        ])
        _models.write({
            'field_id': [(0, 0, {
                'name': self.get_field_name(values['code']),
                'field_description': values.get('name'),
                'ttype': 'many2one',
                'relation': 'account.analytic.tag',
            })],
        })
        # Launch this manually for taking the new dimension field
        self.env["account.invoice.report"].init()
        return res

    def write(self, vals):
        field_vals = {}
        if 'name' in vals or 'code' in vals:
            if 'name' in vals:
                field_vals['field_description'] = vals['name']
            if 'code' in vals:
                field_vals['name'] = self.get_field_name(vals['code'])
            for dimension in self:
                fields_to_update = self.env['ir.model.fields'].search([
                    ('model', 'in', self.get_model_names()),
                    ('name', '=', dimension.get_field_name()),
                ])
                # To avoid 'Can only rename one field at a time!'
                for field_to_update in fields_to_update:
                    field_to_update.write(field_vals)
        return super().write(vals)


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


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['analytic.dimension.line', 'account.analytic.line']
    _analytic_tag_field_name = 'tag_ids'


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['analytic.dimension.line', 'account.move.line']
    _analytic_tag_field_name = 'analytic_tag_ids'


class AccountInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _inherit = ['analytic.dimension.line', 'account.invoice.line']
    _analytic_tag_field_name = 'analytic_tag_ids'
