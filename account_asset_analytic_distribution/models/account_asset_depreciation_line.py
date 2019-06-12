# -*- coding: utf-8 -*-
# Copyright 2019 Abraham Anes - <abraham@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self, post_move=True):
        move_ids = super(AccountAssetDepreciationLine, self).create_move(
            post_move=post_move)
        for line in self:
            asset = line.asset_id
            analytic_distribution = asset.analytic_distribution_id
            category_type = asset.category_id.type
            account = False
            if category_type == 'purchase':
                account = asset.category_id.account_depreciation_expense_id
            elif category_type == 'sale':
                account = asset.category_id.account_depreciation_id
            if line.move_id and analytic_distribution:
                line.move_id.line_ids.filtered(
                    lambda l: l.account_id == account
                ).write({'analytic_distribution_id': analytic_distribution.id})
        return move_ids
