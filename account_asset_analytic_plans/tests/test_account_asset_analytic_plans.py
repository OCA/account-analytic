# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestAccountAssetAnalyticPlans(TransactionCase):
    def test_account_asset_analytic_plans(self):
        asset = self.env.ref('account_asset.account_asset_asset_vehicles0')
        analytics = self.env['account.analytic.plan.instance'].create({
            'name': 'Analytic plan',
            'journal_id': self.env.ref('account.exp').id,
            'account_ids': [
                (0, 0, {
                    'analytic_account_id':
                    self.env.ref('account.analytic_administratif').id,
                    'rate': 50,
                }),
                (0, 0, {
                    'analytic_account_id':
                    self.env.ref('account.analytic_commercial_marketing').id,
                    'rate': 50,
                }),
            ]
        })
        asset.write({'analytics_id': analytics.id})
        asset.depreciation_line_ids[:1].create_move()
        self.assertTrue(asset.mapped('account_move_line_ids.analytics_id'))
