# Copyright 2026 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    source_move_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Source Move Currency",
        readonly=True,
    )
    analytic_percentage = fields.Float(
        readonly=True,
        digits=(16, 2),
        help="Percentage used in the analytic distribution of the source journal item.",
    )
    source_move_line_base_amount = fields.Monetary(
        string="Source Journal Item Base",
        readonly=True,
        currency_field="source_move_currency_id",
        help="Base amount of the source journal item.",
    )
    source_move_base_amount = fields.Monetary(
        string="Source Move Base",
        readonly=True,
        currency_field="source_move_currency_id",
        help="Base amount of the source journal entry.",
    )
    source_move_total_analytic_percentage = fields.Float(
        string="Source Move Analytic Percentage",
        readonly=True,
        digits=(16, 2),
        help="""Percentage of the source move base
        amount represented by this analytic line.""",
    )
