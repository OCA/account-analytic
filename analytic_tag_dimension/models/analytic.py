# -*- coding: utf-8 -*-
# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
# from lxml import etree


class AccountAnalyticDimension(models.Model):
    _name = 'account.analytic.dimension'

    name = fields.Char(
        string='Name',
        required=True)
    code = fields.Char(
        string='Code',
        required=True)
    analytic_tag_ids = fields.One2many(
        comodel_name='account.analytic.tag',
        inverse_name='analytic_dimension_id',
        string='Analytic Tags')

    @api.model
    def create(self, values):
        model_xml_ids = self.env['analytic.dimension.line'].get_models()
        for model_xml_id in model_xml_ids:
            model = self.env.ref(model_xml_id)
            self.env['ir.model.fields'].create({
                'name': 'x_dimension_%s' % (values.get('code')),
                'field_description': values.get('name'),
                'model_id': model.id,
                'ttype': 'many2one',
                'relation': 'account.analytic.tag',
                # 'store': True,
                # 'compute': '_compute_analytic_dimensions'
            })
        return super(AccountAnalyticDimension, self).create(values)


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    analytic_dimension_id = fields.Many2one(
        comodel_name='account.analytic.dimension',
        string='Dimension')

    @api.multi
    def get_dimension_values(self):
        values = {}
        for tag in self.filtered('analytic_dimension_id'):
            code = tag.analytic_dimension_id.code
            values.update({
                'x_dimension_%s' % code: tag.id})
        return values

    def _check_analytic_dimension(self):
        tags_with_dimension = self.filtered('analytic_dimension_id')
        dimensions = tags_with_dimension.mapped('analytic_dimension_id')
        if len(tags_with_dimension) != len(dimensions):
            raise ValidationError(
                _("You can not set two tags from same dimension."))


class AnalyticDimensionLine(models.AbstractModel):
    _name = 'analytic.dimension.line'
    _analytic_tag_field_name = 'analytic_tag_ids'

    @api.model
    def get_models(self):
        # TODO: Is it possible to compute automatically?
        return ['account.model_account_move_line',
                'analytic.model_account_analytic_line',
                'account.model_account_invoice_line',
                'account.model_account_invoice_report']

    @api.model
    def create(self, values):
        result = super(AnalyticDimensionLine, self).create(values)
        if values.get(self._analytic_tag_field_name):
            tag_ids = getattr(
                result, self._analytic_tag_field_name)
            tag_ids._check_analytic_dimension()
            dimension_values = tag_ids.get_dimension_values()
            super(AnalyticDimensionLine, result).write(dimension_values)
        return result

    @api.multi
    def write(self, values):
        result = super(AnalyticDimensionLine, self).write(values)
        if values.get(self._analytic_tag_field_name):
            for record in self:
                tag_ids = getattr(
                    record, self._analytic_tag_field_name
                )
                tag_ids._check_analytic_dimension()
                dimension_values = tag_ids.get_dimension_values()
                super(AnalyticDimensionLine, record).write(dimension_values)
        return result

    # @api.multi
    # def _compute_analytic_dimensions(self):
    #     import pdb; pdb.set_trace()
    #     for record in self:
    #         tag_ids = getattr(record, self._analytic_tag_field_name)
    #         tag_ids._check_analytic_dimension()
    #         for tag in tag_ids:
    #             code = tag.analytic_dimension_id.code
    #             field_name = 'x_dimension_%s' % code
    #             setattr(record, field_name, tag.id)

    # @api.model
    # def fields_view_get(
    #         self, view_id=None, view_type='form',
    #         toolbar=False, submenu=False
    # ):
    #     result = super(AnalyticDimensionLine, self).fields_view_get(
    #         view_id, view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'search':
    #         doc = etree.XML(result['arch'])
    #         dimension_obj = self.env['account.analytic.dimension']
    #         for dimension in dimension_obj.search([]):
    #             field_name = 'x_dimension_%s' % (dimension.code)
    #             doc.append(etree.Element('field', {
    #                 'name': field_name}))
    #         result['arch'] = etree.tostring(doc)
    #     return result


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
