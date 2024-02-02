# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'

    root_id = fields.Many2one('account.analytic.account',
                                   compute="_compute_root_analytic_account",
                                   string="Root Analytic Account",
                                   store=True)

    def _get_root_analytic_account(self):
        self.ensure_one()
        if self.parent_id:
            return self.parent_id._get_root_analytic_account()
        else:
            return self

    @api.depends('parent_id', 'parent_id.root_id')
    def _compute_root_analytic_account(self):
        for account in self:
            account.root_id = account._get_root_analytic_account()
