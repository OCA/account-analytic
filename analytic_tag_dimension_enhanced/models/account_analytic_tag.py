# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    resource_ref = fields.Reference(
        selection=lambda self: [
            (model.model, model.name) for model in self.env["ir.model"].search([])
        ],
        string="Record",
    )

    def _model_skip_required_dimension(self):
        return ["account.payment.register"]

    def condition_required_dimension(self, record):
        """Hooks this method to check condition required dimension"""
        if record._name in self._model_skip_required_dimension():
            return True

        if record._name == "account.move.line" and (record.move_type == "entry" or record.display_type != "product"):
            return True

        if record._name != "account.move.line" and "display_type" in record and record.display_type:
            return True

        return False

    def _check_required_dimension(self, record):
        """Test all required dimension is selected (exclude non-invoice)"""
        record.ensure_one()
        if self.condition_required_dimension(record):
            return
        Dimension = self.env["account.analytic.dimension"]
        req_dimensions = Dimension.search([("required", "=", True)])
        tags_dimension = self.filtered("analytic_dimension_id.required")
        dimensions = tags_dimension.mapped("analytic_dimension_id")
        missing = req_dimensions - dimensions
        if missing:
            raise ValidationError(
                self.env._("Following dimension(s) not selected: %s")
                % ", ".join(missing.mapped("name"))
            )
