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
        for rec in self:
            domain_result = rec._dynamic_domain_analytic_tags()
            domain = domain_result.get("domain", {}).get(
                rec._analytic_tag_field_name, []
            )
            rec.domain_tag_ids = domain[0][2] if domain else []

    def _dynamic_domain_analytic_tags(self):
        """
        - For dimension without by_sequence, always show
        - For dimension with by_sequence, only show tags by sequence
        - Option to filter next dimension based on selected_tags
        """
        Dimension = self.env["account.analytic.dimension"]
        Tag = self.env["account.analytic.tag"]

        # If no dimension uses sequence, show everything (no filter)
        if not Dimension.search_count([("by_sequence", "=", True)]):
            return {"domain": {self._analytic_tag_field_name: []}}

        # Tags from non-sequenced dimensions (always shown)
        base_tags = Tag.search(
            [
                "|",
                ("analytic_dimension_id", "=", False),
                ("analytic_dimension_id.by_sequence", "=", False),
            ]
        )

        # Find next dimension by_sequence
        selected_tags = self[self._analytic_tag_field_name]
        selected_dimensions = selected_tags.mapped("analytic_dimension_id").filtered(
            "by_sequence"
        )
        current_max_seq = max(selected_dimensions.mapped("sequence"), default=-1)

        next_dimension = Dimension.search(
            [("by_sequence", "=", True), ("sequence", ">", current_max_seq)],
            order="sequence",
            limit=1,
        )
        next_tag_ids = []
        if next_dimension and next_dimension.filtered_field_ids:
            # Filetered by previously selected_tags
            next_tag_list = []
            for field in next_dimension.filtered_field_ids:
                matched_tags = selected_tags.filtered(
                    lambda tag, field=field: tag.resource_ref
                    and tag.resource_ref._name == field.relation
                )
                matched_ids = [ref.id for ref in matched_tags.mapped("resource_ref")]
                dimension_tag_ids = next_dimension.analytic_tag_ids.filtered(
                    lambda tag, field=field, matched_ids=matched_ids: tag.resource_ref
                    and tag.resource_ref[field.name].id in matched_ids
                ).ids
                next_tag_list.append(set(dimension_tag_ids))
            # "&" to all in next_tag_list
            if next_tag_list:
                next_tag_ids = list(set.intersection(*next_tag_list))
        else:
            next_tag_ids = next_dimension.analytic_tag_ids.ids

        # Tags from non by_sequence dimension and next dimension
        all_tag_ids = base_tags.ids + next_tag_ids
        domain = [("id", "in", all_tag_ids)]
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
