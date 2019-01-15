# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self):
        """create analytic lines according to analytic plan if it is set"""
        # support account_analytic{,_plan}_required
        user_types = self.mapped(
            'asset_id.category_id.account_expense_depreciation_id.user_type',
        )
        policy_per_type = {}
        if 'analytic_policy' in user_types._fields:
            for user_type in user_types:
                if user_type.analytic_policy == 'optional':
                    continue
                policy_per_type[user_type] = user_type.analytic_policy
                user_type.update({'analytic_policy': 'optional'})

        result = super(AccountAssetDepreciationLine, self).create_move()

        for user_type, policy in policy_per_type.items():
            user_type.update({'analytic_policy': policy})

        for this in self:
            asset = this.asset_id
            account = asset.category_id.account_expense_depreciation_id
            analytics = asset.analytics_id or asset.category_id.analytics_id
            if not analytics and account.user_type not in policy_per_type:
                continue
            move_line = this.move_id.line_id.filtered(
                lambda x: x.account_id == account
            )
            move_line.write({
                'analytics_id': analytics.id,
            })
            move_line.create_analytic_lines()
            # rerun validation if we changed types above
            if policy_per_type:
                move_line._validate_fields([
                    'account_id', 'analytic_account_id', 'analytics_id',
                    'credit', 'debit',
                ])
        return result
