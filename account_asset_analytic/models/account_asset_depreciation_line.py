# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self, post_move=True):
        move_ids = super(AccountAssetDepreciationLine, self).create_move(
            post_move=post_move)
        for line in self:
            asset = line.asset_id
            analytic = asset.analytic_account_id
            category_type = asset.category_id.type
            account = False
            if category_type == 'purchase':
                account = asset.category_id.account_depreciation_expense_id
            elif category_type == 'sale':
                account = asset.category_id.account_depreciation_id
            if line.move_id and analytic:
                line.move_id.line_ids.filtered(
                    lambda x: x.account_id == account).write({
                        'analytic_account_id': analytic.id})
        return move_ids
