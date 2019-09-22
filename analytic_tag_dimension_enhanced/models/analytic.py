# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountAnalyticDimension(models.Model):
    _inherit = 'account.analytic.dimension'

    ref_model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Ref Model',
        help="Select model if you want to use it to create analytic tags, "
        "each tag will have reference to the data record in that model.\n"
        "For example, if you select Department (hr.department) then click "
        "Create Tags button, tags will be created from each department "
        " and also has resource_ref to the department record",
    )
    filtered_field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string='Filtered by fields',
        domain="[('model_id', '=', ref_model_id),"
        "('ttype', '=', 'many2one')]",
        help="Filtered listing tags by fields of this model, based on value "
        "of selected analytic tags in working document",
    )
    required = fields.Boolean(
        string='Required',
        default=False,
        help="If required, this dimension needed to be "
        "selected in working document",
    )
    by_sequence = fields.Boolean(
        default=False,
        help="If checked, this dimemsion's tags will be available "
        "only when previous dimension's tags is selected",
    )
    sequence = fields.Integer(
        help="This field works with By Sequence",
    )

    @api.constrains('by_sequence', 'sequence')
    def _check_sequence(self):
        seq_list = self.search([('by_sequence', '=', True)]).mapped('sequence')
        if len(seq_list) != len(set(seq_list)):
            raise ValidationError(_('Duplicated dimension sequences'))

    def create_analytic_tags(self):
        """Helper function to create tags based on ref_model_id"""
        self.ensure_one()
        if not self.ref_model_id:
            return
        Tag = self.env['account.analytic.tag']
        model = self.ref_model_id.model
        TagModel = self.env[model]
        # Delete orphan tags
        self.analytic_tag_ids.filtered(lambda l: not l.resource_ref or
                                       l.resource_ref._name != model).unlink()
        tag_res_ids = [x.resource_ref.id for x in self.analytic_tag_ids]
        recs = TagModel.search([('id', 'not in', tag_res_ids)])
        for rec in recs:
            Tag.create({'name': rec.display_name,
                        'analytic_dimension_id': self.id,
                        'resource_ref': '%s,%s' % (model, rec.id)})


class AnalyticDimensionLine(models.AbstractModel):
    _inherit = 'analytic.dimension.line'

    domain_tag_ids = fields.Many2many(
        comodel_name='account.analytic.tag',
        compute='_compute_analytic_tags_domain',
        help="Helper field, the filtered tags_ids when record is saved",
    )

    @api.depends(lambda self: (self._analytic_tag_field_name,)
                 if self._analytic_tag_field_name else ())
    def _compute_analytic_tags_domain(self):
        res = {}
        for rec in self:
            tag_ids = []
            res = rec._dynamic_domain_analytic_tags()
            if res['domain'][self._analytic_tag_field_name]:
                tag_ids = res['domain'][self._analytic_tag_field_name][0][2]
            rec.domain_tag_ids = tag_ids
        return res

    def _dynamic_domain_analytic_tags(self):
        """
        - For dimension without by_sequence, always show
        - For dimension with by_sequence, only show tags by sequence
        - Option to filter next dimension based on selected_tags
        """
        Dimension = self.env['account.analytic.dimension']
        Tag = self.env['account.analytic.tag']
        # If no dimension with by_sequence, nothing to filter, exist
        count = Dimension.search_count([('by_sequence', '=', True)])
        if count == 0:
            return {'domain': {self._analytic_tag_field_name: []}}
        # Find non by_sequence tags, to show always
        tags = Tag.search(['|', ('analytic_dimension_id', '=', False),
                           ('analytic_dimension_id.by_sequence', '=', False)])
        # Find next dimension by_sequence
        selected_tags = self[self._analytic_tag_field_name]
        sequences = selected_tags.mapped('analytic_dimension_id').\
            filtered('by_sequence').mapped('sequence')
        cur_sequence = sequences and max(sequences) or -1
        next_dimension = Dimension.search(
            [('by_sequence', '=', True), ('sequence', '>', cur_sequence)],
            order='sequence', limit=1)
        next_tag_ids = []
        if next_dimension and next_dimension.filtered_field_ids:
            # Filetered by previously selected_tags
            next_tag_list = []
            for field in next_dimension.filtered_field_ids:
                matched_tags = selected_tags.filtered(
                    lambda l: l.resource_ref and
                    l.resource_ref._name == field.relation)
                tag_resources = matched_tags.mapped('resource_ref')
                res_ids = tag_resources and tag_resources.ids or []
                tag_ids = next_dimension.analytic_tag_ids.filtered(
                    lambda l: l.resource_ref[field.name].id in res_ids).ids
                next_tag_list.append(set(tag_ids))
            # "&" to all in next_tag_list
            next_tag_ids = list(set.intersection(*map(set, next_tag_list)))
        else:
            next_tag_ids = next_dimension.analytic_tag_ids.ids
        # Tags from non by_sequence dimension and next dimension
        tag_ids = tags.ids + next_tag_ids
        # tag_ids = tags.ids + next_tag_ids
        domain = [('id', 'in', tag_ids)]
        return {'domain': {self._analytic_tag_field_name: domain}}


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    resource_ref = fields.Reference(
        selection=lambda self: [(model.model, model.name)
                                for model in self.env['ir.model'].search([])],
        string='Record',
    )

    def _check_analytic_dimension(self):
        super()._check_analytic_dimension()
        # Test all required dimension is selected
        Dimension = self.env['account.analytic.dimension']
        req_dimensions = Dimension.search([('required', '=', True)])
        tags_dimension = self.filtered('analytic_dimension_id.required')
        dimensions = tags_dimension.mapped('analytic_dimension_id')
        missing = req_dimensions - dimensions
        if missing:
            raise ValidationError(
                _("Following dimension(s) not selected: "
                  "%s") % ', '.join(missing.mapped('name')))
