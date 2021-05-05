# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticDimension(models.Model):
    _inherit = "account.analytic.dimension"

    ref_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Ref Model",
        help="Select model if you want to use it to create analytic tags, "
        "each tag will have reference to the data record in that model.\n"
        "For example, if you select Department (hr.department) then click "
        "Create Tags button, tags will be created from each department "
        " and also has resource_ref to the department record",
    )
    filtered_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Filtered by fields",
        domain="[('model_id', '=', ref_model_id), ('ttype', '=', 'many2one')]",
        help="Filtered listing tags by fields of this model, based on value "
        "of selected analytic tags in working document",
    )
    required = fields.Boolean(
        string="Required",
        default=False,
        help="If required, this dimension needed to be selected in working document",
    )
    by_sequence = fields.Boolean(
        default=False,
        help="If checked, this dimemsion's tags will be available "
        "only when previous dimension's tags is selected",
    )
    sequence = fields.Integer(
        help="This field works with By Sequence",
    )

    @api.constrains("by_sequence", "sequence")
    def _check_sequence(self):
        seq_list = self.search([("by_sequence", "=", True)]).mapped("sequence")
        if len(seq_list) != len(set(seq_list)):
            raise ValidationError(_("Duplicated dimension sequences"))

    def create_analytic_tags(self):
        """Helper function to create tags based on ref_model_id"""
        self.ensure_one()
        if not self.ref_model_id:
            return
        Tag = self.env["account.analytic.tag"]
        model = self.ref_model_id.model
        TagModel = self.env[model]
        # Delete orphan tags
        self.analytic_tag_ids.filtered(
            lambda l: not l.resource_ref or l.resource_ref._name != model
        ).unlink()
        tag_res_ids = [x.resource_ref.id for x in self.analytic_tag_ids]
        recs = TagModel.search([("id", "not in", tag_res_ids)])
        vals_dict = [
            {
                "name": rec.display_name,
                "analytic_dimension_id": self.id,
                "resource_ref": "{},{}".format(model, rec.id),
            }
            for rec in recs
        ]
        Tag.create(vals_dict)
