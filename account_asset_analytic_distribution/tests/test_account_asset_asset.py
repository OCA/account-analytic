# -*- coding: utf-8 -*-
# Copyright 2019 Abraham Anes - <abraham@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta, datetime

from odoo.tests.common import SavepointCase
from odoo import fields


class TestAccountAssetAnalyticDistribution(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountAssetAnalyticDistribution, cls).setUpClass()

        # Create journal
        cls.journal = cls.env['account.journal'].create({
            'name': 'Name test',
            'code': 'Code test',
            'type': 'general',
        })
        # Create account type
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Account type test',
            'type': 'other',
        })
        # Create account asset
        cls.account_asset = cls.env['account.account'].create({
            'code': 'Code test',
            'name': 'Name test',
            'user_type_id': cls.account_type.id,
        })
        # Create account depreciation
        cls.account_depreciation = cls.env['account.account'].create({
            'code': 'Code ad test',
            'name': 'Name test',
            'user_type_id': cls.account_type.id,
        })
        # Create account depreciation expense
        cls.account_depreciation_expense = cls.env[
            'account.account'
        ].create({
            'code': 'Code ade test',
            'name': 'Name test',
            'user_type_id': cls.account_type.id,
        })
        # Create asset category analytic account
        cls.category_analytic_account = cls.env[
            'account.analytic.account'
        ].create({
            'name': 'Category analytic account test',
        })
        # Create asset category
        cls.asset_category = cls.env['account.asset.category'].create({
            'name': 'Asset category test',
            'journal_id': cls.journal.id,
            'account_asset_id': cls.account_asset.id,
            'account_depreciation_id': cls.account_depreciation.id,
            'account_depreciation_expense_id':
                cls.account_depreciation_expense.id,
            'method_number': 5,
            'method_period': 12,
        })
        date_time = fields.Datetime.to_string(
            datetime.now() - timedelta(hours=1))
        # Create asset analytic distribution
        cls.asset_analytic_distribution = cls.env[
            'account.analytic.distribution'
        ].create({
            'name': 'Asset analytic distribution test',
        })
        # Create asset
        cls.asset = cls.env['account.asset.asset'].create({
            'name': 'Asset test',
            'category_id': cls.asset_category.id,
            'date': date_time,
            'value': 10000,
            'analytic_distribution_id': cls.asset_analytic_distribution.id,
        })
        # Create a partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        # Create invoice
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Test line',
                    'asset_category_id': cls.asset_category.id,
                    'analytic_distribution_id':
                        cls.asset_analytic_distribution.id,
                    'account_id': cls.asset_category.account_asset_id.id,
                    'quantity': 10.0,
                    'price_unit': 50.0,
                })
            ]
        })

    def test_flow_asset(self):
        self.asset.validate()
        self.asset.depreciation_line_ids[0].create_move()
        move = self.asset.depreciation_line_ids[0].move_id
        move.post()
        analytic_distributions = move.mapped(
            'line_ids.analytic_distribution_id')
        for analytic_distribution in analytic_distributions:
            self.assertEqual(
                analytic_distribution,
                self.asset.analytic_distribution_id,
                '''analytic distribution has not been propagated
                   to the move line'''
            )

    def test_flow_invoice(self):
        self.invoice.action_invoice_open()
        invoice_lines = self.invoice.invoice_line_ids
        for invoice_line in invoice_lines:
            asset = self.env['account.asset.asset'].search([
                ('code', '=', invoice_line.invoice_id.number),
                ('company_id', '=', invoice_line.company_id.id),
            ], limit=1)
            self.assertEqual(
                asset.analytic_distribution_id,
                invoice_line.analytic_distribution_id,
                'analytic distribution has not been propagated to the asset'
            )
