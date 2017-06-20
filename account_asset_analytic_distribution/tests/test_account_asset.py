# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestAccountAsset(TransactionCase):
    def setUp(self):
        super(TestAccountAsset, self).setUp()
        # Create a payable account for suppliers
        self.account_suppliers = self.env['account.account'].create({
            'name': 'Suppliers',
            'code': '410000',
            'type': 'other',
            'user_type': self.env.ref('account.data_account_type_payable').id,
            'reconcile': True,
        })
        # Create a supplier
        self.supplier = self.env['res.partner'].create({
            'name': 'Asset provider',
            'supplier': True,
            'customer': False,
        })
        # Create an analytic journal for purchases
        self.analytic_journal_purchase = self.env['account.analytic.journal'].\
            create({
                'name': 'Purchase analytic journal',
                'code': 'PRCH',
                'type': 'purchase',
            })
        # Create a journal for purchases
        self.journal_purchase = self.env['account.journal'].create({
            'name': 'Purchase journal',
            'code': 'PRCH',
            'type': 'purchase',
            'analytic_journal_id': self.analytic_journal_purchase.id,
        })
        # Create an analytic journal for assets
        self.analytic_journal_asset = self.env['account.analytic.journal'].\
            create({
                'name': 'Asset analytic journal',
                'code': 'JRNL',
                'type': 'general',
            })
        # Create a journal for assets
        self.journal_asset = self.env['account.journal'].create({
            'name': 'Asset journal',
            'code': 'JRNL',
            'type': 'general',
            'analytic_journal_id': self.analytic_journal_asset.id,
        })
        # Create an account for assets
        self.account_asset = self.env['account.account'].create({
            'name': 'Asset',
            'code': '216000',
            'type': 'other',
            'user_type': self.env.ref('account.data_account_type_asset').id,
            'reconcile': False,
        })
        # Create an account for assets dereciation
        self.account_asset_depreciation = self.env['account.account'].create({
            'name': 'Asset depreciation',
            'code': '281600',
            'type': 'other',
            'user_type': self.env.ref('account.data_account_type_asset').id,
            'reconcile': False,
        })
        # Create an account for assets expense
        self.account_asset_expense = self.env['account.account'].create({
            'name': 'Asset expense',
            'code': '681000',
            'type': 'other',
            'user_type': self.env.ref('account.data_account_type_expense').id,
            'reconcile': False,
        })
        # Create an analytic account A
        self.analytic_a = self.env['account.analytic.account'].create({
            'name': 'Asset Analytic A',
            'type': 'normal',
        })
        # Create an analytic account B
        self.analytic_b = self.env['account.analytic.account'].create({
            'name': 'Asset Analytic B',
            'type': 'normal',
        })
        # Create an assset category, with analytic account A
        self.asset_category = self.env['account.asset.category'].create({
            'name': 'Asset category for testing',
            'journal_id': self.journal_asset.id,
            'account_asset_id': self.account_asset.id,
            'account_depreciation_id': self.account_asset_depreciation.id,
            'account_expense_depreciation_id': self.account_asset_expense.id,
            'account_analytic_id': self.analytic_a.id,
        })
        # Create an invoice
        self.asset_name = 'Office table'
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.supplier.id,
            'account_id': self.account_suppliers.id,
            'journal_id': self.journal_purchase.id,
            'reference_type': 'none',
            'reference': 'PURCHASE/12345',
            'invoice_line': [
                (0, False, {
                    'name': self.asset_name,
                    'account_id': self.account_asset.id,
                    'account_analytic_id': self.analytic_b.id,
                    'asset_category_id': self.asset_category.id,
                    'quantity': 1.0,
                    'price_unit': 100.00,
                }),
            ],
        })
        # Validate invoice
        self.invoice.signal_workflow('invoice_open')

    def test_asset_create(self):
        # Search asset created
        asset = self.env['account.asset.asset'].search([
            ('code', '=', self.invoice.number),
        ])
        # Asset must be created with code == invoice number
        self.assertTrue(asset)
        # Asset name must be invoice line description
        self.assertEqual(self.asset_name, asset.name)
        # Asset category must be the one selected in invoice line
        self.assertEqual(self.asset_category.id, asset.category_id.id)
        # Asset purchase date must be invoice date
        self.assertEqual(self.invoice.date_invoice, asset.purchase_date)
        # Asset analytic account must be invoice line analytic account
        self.assertEqual(self.analytic_b.id, asset.analytic_account_id.id)

    def test_move_create(self):
        # Search asset created
        asset = self.env['account.asset.asset'].search([
            ('code', '=', self.invoice.number),
        ])
        # Asset must be created with code == invoice number
        self.assertTrue(asset)
        line = asset.depreciation_line_ids.filtered(
            lambda x: x.move_check is False)[0]
        line.create_move()
        # Journal entry must be created
        self.assertTrue(line.move_id)
        # Expense journal item analytic account must be asset analytic account
        expense = line.move_id.line_id.filtered(
            lambda x: x.account_id == self.account_asset_expense)[0]
        self.assertEqual(self.analytic_b.id, expense.analytic_account_id.id)
