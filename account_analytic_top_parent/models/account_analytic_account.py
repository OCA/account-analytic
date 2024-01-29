# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class AccountAnalytic(models.Model):
    _inherit = "account.analytic.account"

    top_parent_id = fields.Many2one(
        "account.analytic.account",
        compute="_compute_top_parent_analytic_account",
        string="Top Parent Analytic Account",
        store=True,
    )

    def _get_top_parent_analytic_account(self):
        self.ensure_one()
        if self.parent_id:
            return self.parent_id._get_top_parent_analytic_account()
        else:
            return self

    @api.depends("parent_id", "parent_id.top_parent_id")
    def _compute_top_parent_analytic_account(self):
        for account in self:
            account.top_parent_id = account._get_top_parent_analytic_account()
