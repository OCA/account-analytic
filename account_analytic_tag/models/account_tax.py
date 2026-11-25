# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import Command, api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_base_line_tax_repartition_grouping_key(
        self, base_line, base_line_grouping_key, tax_data, tax_rep_data
    ):
        # Include the analytic tags of the base line in the tax line, following the
        # same criteria as the analytic distribution: when the tax is flagged to be
        # included in the analytic cost, or the repartition line has no account.
        grouping_key = super()._prepare_base_line_tax_repartition_grouping_key(
            base_line, base_line_grouping_key, tax_data, tax_rep_data
        )
        tags = self.env["account.analytic.tag"]
        tax = tax_data["tax"]
        tax_rep = tax_rep_data["tax_rep"]
        if tax.analytic or not tax_rep.use_in_tax_closing:
            tags = getattr(base_line["record"], "analytic_tag_ids", tags)
        grouping_key["analytic_tag_ids"] = [Command.set(tags.ids)]
        return grouping_key

    @api.model
    def _prepare_tax_line_repartition_grouping_key(self, tax_line):
        # Keep the same key on existing tax lines so they are updated, not recreated.
        grouping_key = super()._prepare_tax_line_repartition_grouping_key(tax_line)
        tags = getattr(
            tax_line["record"], "analytic_tag_ids", self.env["account.analytic.tag"]
        )
        grouping_key["analytic_tag_ids"] = [Command.set(tags.ids)]
        return grouping_key
