# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AnalyticLineSplitWizard(models.TransientModel):
    _name = "analytic.line.split.wizard"
    _description = "Analytic Line Split Wizard"

    def _get_default_line_id(self):
        analytic_line_id = self.env.context.get("active_id")
        return self.env["account.analytic.line"].browse(analytic_line_id)

    def _get_default_amount(self):
        return self.env.context.get("amount")

    def _get_default_account_id(self):
        account_analytic_id = self.env.context.get("account_id")
        return self.env["account.analytic.account"].browse(account_analytic_id)

    line_id = fields.Many2one(
        comodel_name="account.analytic.line",
        string="Analytic Line",
        default=_get_default_line_id,
        readonly=True,
    )
    name = fields.Char(
        string="Name",
        related="account_id.name",
        readonly=True,
    )
    amount_total = fields.Float(
        string="Amount Total",
        default=_get_default_amount,
        readonly=True,
    )
    percentage = fields.Float(
        string="Percentage", default=100.0, readonly=True, compute="_compute_percentage"
    )
    amount = fields.Float(
        string="Amount",
        default=_get_default_amount,
        readonly=True,
        compute="_compute_amount",
    )
    account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        default=_get_default_account_id,
        readonly=True,
    )
    analytic_line_split_ids = fields.One2many(
        comodel_name="analytic.line.split",
        string="Analytic Lines",
        inverse_name="wizard_id",
    )

    @api.depends("analytic_line_split_ids")
    def _compute_percentage(self):
        for line in self:
            total_percentage = sum(
                line_split.percentage for line_split in line.analytic_line_split_ids
            )
            line.percentage = 100 - total_percentage

    @api.depends("analytic_line_split_ids")
    def _compute_amount(self):
        for line in self:
            line.amount = line.amount_total * (line.percentage / 100)

    @api.onchange("analytic_line_split_ids")
    def _onchange_analytic_line_split_ids(self):
        total_percentage = sum(line.percentage for line in self.analytic_line_split_ids)
        if total_percentage > 100:
            raise ValidationError(_("The total percentage cannot exceed 100%!"))

    def action_split_line(self):
        self.line_id.write(
            {
                "amount": self.amount,
            }
        )
        for line in self.analytic_line_split_ids:
            copy_line_id = self.line_id.copy()
            copy_line_id.write(
                {
                    "account_id": line.account_id,
                    "amount": line.amount,
                    "parent_id": self.line_id,
                }
            )


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
            if not (0 < line.percentage <= 100):
                raise ValidationError(
                    _(
                        "Percentage must be greater than 0 and less than or equal to 100."
                    )
                )

    @api.depends("wizard_id.amount_total", "percentage")
    def _compute_amount(self):
        for line in self:
            line.amount = line.wizard_id.amount_total * (line.percentage / 100)
