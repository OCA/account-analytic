# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticDimension(models.Model):
    _inherit = "account.analytic.dimension"

    ref_model_id = fields.Many2one(
        comodel_name="ir.model",
        help="Select model if you want to use it to create analytic tags, "
        "each tag will have reference to the data record in that model.\n"
        "For example, if you select Department (hr.department) then click "
        "Create Tags button, tags will be created from each department "
        " and also has resource_ref to the department record",
    )
    filtered_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Filtered by fields",
        help="Filtered listing tags by fields of this model, based on value "
        "of selected analytic tags in working document",
    )
    required = fields.Boolean(
        help="If required, this dimension needed to be selected in working document",
    )
    by_sequence = fields.Boolean(
        help="If checked, this dimemsion's tags will be available "
        "only when previous dimension's tags is selected",
    )
    sequence = fields.Integer(
        help="This field works with By Sequence",
    )

    @api.constrains("by_sequence", "sequence")
    def _check_sequence(self):
        records = self.search_read([("by_sequence", "=", True)], fields=["sequence"])
        seq_list = [rec["sequence"] for rec in records]
        if len(seq_list) != len(set(seq_list)):
            raise ValidationError(self.env._("Duplicated dimension sequences"))

    def create_analytic_tags(self):
        """Helper function to create analytic tags based on ref_model_id"""
        self.ensure_one()
        if not self.ref_model_id:
            return

        Tag = self.env["account.analytic.tag"]
        model = self.ref_model_id.model
        TagModel = self.env[model]

        # Delete orphan tags
        orphan_tags = self.analytic_tag_ids.filtered(
            lambda tag, model=model: not tag.resource_ref
            or tag.resource_ref._name != model
        )
        if orphan_tags:
            orphan_tags.unlink()

        # Update name analytic tag from Ref model.
        for tag in self.analytic_tag_ids:
            if tag.resource_ref and tag.display_name != tag.resource_ref.display_name:
                tag.name = tag.resource_ref.display_name

        # Create missing analytic tags
        existing_ref_ids = {
            tag.resource_ref.id for tag in self.analytic_tag_ids if tag.resource_ref
        }
        missing_recs = TagModel.search([("id", "not in", list(existing_ref_ids))])

        if missing_recs:
            vals_dict = [
                {
                    "name": rec.display_name,
                    "analytic_dimension_id": self.id,
                    "resource_ref": f"{model},{rec.id}",
                }
                for rec in missing_recs
            ]
            Tag.create(vals_dict)
