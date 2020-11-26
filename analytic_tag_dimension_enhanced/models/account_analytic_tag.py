# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    resource_ref = fields.Reference(
        selection=lambda self: [
            (model.model, model.name) for model in self.env["ir.model"].search([])
        ],
        string="Record",
    )

    def _check_required_dimension(self, record):
        """ Test all required dimension is selected (exclude non-invoice) """
        record.ensure_one()
        if "exclude_from_invoice_tab" in record and record.exclude_from_invoice_tab:
            return
        Dimension = self.env["account.analytic.dimension"]
        req_dimensions = Dimension.search([("required", "=", True)])
        tags_dimension = self.filtered("analytic_dimension_id.required")
        dimensions = tags_dimension.mapped("analytic_dimension_id")
        missing = req_dimensions - dimensions
        if missing:
            raise ValidationError(
                _("Following dimension(s) not selected: %s")
                % ", ".join(missing.mapped("name"))
            )
