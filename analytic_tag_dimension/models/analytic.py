# -*- coding: utf-8 -*-
# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


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
        model_xml_ids = ['account.model_account_move_line',
                         'analytic.model_account_analytic_line']
        for model_xml_id in model_xml_ids:
            model = self.env.ref(model_xml_id)
            self.env['ir.model.fields'].create({
                'name': 'x_dimension_%s' % (values.get('code')),
                'field_description': values.get('name'),
                'model_id': model.id,
                'ttype': 'many2one',
                'relation': 'account.analytic.tag'
            })
        return super(AccountAnalyticDimension, self).create(values)


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    analytic_dimension_id = fields.Many2one(
        comodel_name='account.analytic.dimension',
        string='Dimension',
        required=True)

    @api.multi
    def get_dimension_values(self):
        values = {}
        for tag in self:
            code = tag.analytic_dimension_id.code
            values.update({
                'x_dimension_%s' % code: tag.id})
        return values


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.constrains('tag_ids')
    def _check_field(self):
        dimension_ids = self.tag_ids.mapped('analytic_dimension_id').ids
        if len(self.tag_ids.ids) != len(dimension_ids):
            raise ValidationError(
                _("You can not set two tags from same dimension."))

    @api.model
    def create(self, values):
        tag_values = values.get('tag_ids')
        # tag_ids can not be created from here
        if tag_values:
            tag_ids = tag_values[0][2]
            tag_obj = self.env['account.analytic.tag']
            values.update(tag_obj.browse(tag_ids).get_dimension_values())
        return super(AccountAnalyticLine, self).create(values)

    @api.multi
    def write(self, values):
        tag_values = values.get('tag_ids')
        # tag_ids can not be created from here
        if tag_values:
            tag_ids = tag_values[0][2]
            tag_obj = self.env['account.analytic.tag']
            values.update(tag_obj.browse(tag_ids).get_dimension_values())
        return super(AccountAnalyticLine, self).write(values)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('analytic_tag_ids')
    def _check_field(self):
        dimension_ids = self.analytic_tag_ids.mapped(
            'analytic_dimension_id').ids
        if len(self.analytic_tag_ids.ids) != len(dimension_ids):
            raise ValidationError(
                _("You can not set two tags from same dimension."))

    @api.model
    def create(self, values):
        tag_values = values.get('analytic_tag_ids')
        # tag_ids can not be created from here
        if tag_values:
            tag_ids = tag_values[0][2]
            tag_obj = self.env['account.analytic.tag']
            values.update(tag_obj.browse(tag_ids).get_dimension_values())
        return super(AccountMoveLine, self).create(values)

    @api.multi
    def write(self, values):
        tag_values = values.get('analytic_tag_ids')
        # tag_ids can not be created from here
        if tag_values:
            tag_ids = tag_values[0][2]
            tag_obj = self.env['account.analytic.tag']
            values.update(tag_obj.browse(tag_ids).get_dimension_values())
        return super(AccountMoveLine, self).write(values)
