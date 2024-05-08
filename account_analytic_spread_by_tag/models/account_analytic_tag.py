# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    to_spread = fields.Boolean(
        string="Spread analytic amounts",
        help="If enabled, the move line amounts using this tag will be spread across \
            all the analytic accounts that use this same tag.",
    )
    spread_filter_operation = fields.Selection(
        string="Operation", selection=[("include", "Include"), ("exclude", "Exclude")]
    )
    spread_filter_analytic_account_ids = fields.Many2many(
        comodel_name="account.analytic.account",
        relation="account_analytic_tag_account_filter_rel",
        string="Analytic Accounts",
    )
