# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AnalyticLineSplit(models.TransientModel):
    _name = "analytic.line.split"
    _description = "Analytic Line Split"

    def _get_default_line_id(self):
        analytic_line_id = self.env.context.get("line_id")
        return self.env["account.analytic.line"].browse(analytic_line_id)

    wizard_id = fields.Many2one(
        comodel_name="analytic.line.split.wizard",
        required=True,
        ondelete="cascade",
    )
    line_id = fields.Many2one(
        comodel_name="account.analytic.line",
        string="Analytic Line",
        readonly=True,
        default=_get_default_line_id,
    )
    name = fields.Char(
        string="Name",
        related="account_id.name",
        readonly=True,
    )
    account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        required=True,
    )
    percentage = fields.Float(
        string="Percentage",
        required=True,
        default=0.0,
    )
    amount = fields.Float(
        string="Amount",
        readonly=True,
        compute="_compute_amount",
        store=True,
    )

    @api.constrains("percentage")
    def _check_percentage(self):
        for line in self:
            if not (0 < line.percentage < 100):
                raise ValidationError(
                    _("Percentage must be greater than 0 and less than 100.")
                )

    @api.depends("wizard_id.amount_total", "percentage")
    def _compute_amount(self):
        for line in self:
            line.amount = line.wizard_id.amount_total * (line.percentage / 100)
