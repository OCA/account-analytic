# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AnalyticDimensionLine(models.AbstractModel):
    _inherit = "analytic.dimension.line"

    domain_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        compute="_compute_analytic_tags_domain",
        help="Helper field, the filtered tags_ids when record is saved",
    )

    @api.depends(
        lambda self: (self._analytic_tag_field_name,)
        if self._analytic_tag_field_name
        else ()
    )
    def _compute_analytic_tags_domain(self):
        res = {}
        for rec in self:
            tag_ids = []
            res = rec._dynamic_domain_analytic_tags()
            if res["domain"][self._analytic_tag_field_name]:
                tag_ids = res["domain"][self._analytic_tag_field_name][0][2]
            rec.domain_tag_ids = tag_ids
        return res

    def _dynamic_domain_analytic_tags(self):
        """
        - For dimension without by_sequence, always show
        - For dimension with by_sequence, only show tags by sequence
        - Option to filter next dimension based on selected_tags
        """
        Dimension = self.env["account.analytic.dimension"]
        Tag = self.env["account.analytic.tag"]
        # If no dimension with by_sequence, nothing to filter, exist
        count = Dimension.search_count([("by_sequence", "=", True)])
        if count == 0:
            return {"domain": {self._analytic_tag_field_name: []}}
        # Find non by_sequence tags, to show always
        tags = Tag.search(
            [
                "|",
                ("analytic_dimension_id", "=", False),
                ("analytic_dimension_id.by_sequence", "=", False),
            ]
        )
        # Find next dimension by_sequence
        selected_tags = self[self._analytic_tag_field_name]
        sequences = (
            selected_tags.mapped("analytic_dimension_id")
            .filtered("by_sequence")
            .mapped("sequence")
        )
        cur_sequence = sequences and max(sequences) or -1
        next_dimension = Dimension.search(
            [("by_sequence", "=", True), ("sequence", ">", cur_sequence)],
            order="sequence",
            limit=1,
        )
        next_tag_ids = []
        if next_dimension and next_dimension.filtered_field_ids:
            # Filetered by previously selected_tags
            next_tag_list = []
            for field in next_dimension.filtered_field_ids:
                matched_tags = selected_tags.filtered(
                    lambda l: l.resource_ref and l.resource_ref._name == field.relation
                )
                tag_resources = matched_tags.mapped("resource_ref")
                res_ids = tag_resources and [x.id for x in tag_resources] or []
                tag_ids = next_dimension.analytic_tag_ids.filtered(
                    lambda l: l.resource_ref[field.name].id in res_ids
                ).ids
                next_tag_list.append(set(tag_ids))
            # "&" to all in next_tag_list
            next_tag_ids = list(set.intersection(*map(set, next_tag_list)))
        else:
            next_tag_ids = next_dimension.analytic_tag_ids.ids
        # Tags from non by_sequence dimension and next dimension
        tag_ids = tags.ids + next_tag_ids
        # tag_ids = tags.ids + next_tag_ids
        domain = [("id", "in", tag_ids)]
        return {"domain": {self._analytic_tag_field_name: domain}}

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
