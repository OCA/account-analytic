# Copyright 2020 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common
from datetime import datetime


class TestAssetAnalyticAccount(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAssetAnalyticAccount, cls).setUpClass()

        cls.asset = cls.env["account.asset.asset"]
        cls.asset_category = cls.env["account.asset.category"]
        cls.journal = cls.env["account.journal"]
        cls.account = cls.env["account.account"]
        cls.acc_type = cls.env["account.account.type"]
        cls.aa_obj = cls.env["account.analytic.account"]

        # Create journal, accounts, asset category, analytic account
        cls.journal_sale = cls.journal.create({
            'name': 'Sale Journal',
            'type': 'sale',
            'code': 'SALE',
        })
        cls.journal_purchase = cls.journal.create({
            'name': 'Purchase Journal',
            'type': 'purchase',
            'code': 'PURCHASE',
        })
        cls.acc_type_sale = cls.acc_type.create({
            'name': 'Sale Type ACC',
            'type': 'receivable',
        })
        cls.acc_type_purchase = cls.acc_type.create({
            'name': 'Purchase Type ACC',
            'type': 'payable',
        })
        cls.account_sale = cls.account.create({
            'name':
            'Sale acc',
            'code':
            '10000000',
            'user_type_id':
            cls.acc_type_sale.id,
            'reconcile':
            True,
        })
        cls.account_purchase = cls.account.create({
            'name':
            'Purchase acc',
            'code':
            '10000001',
            'user_type_id':
            cls.acc_type_purchase.id,
            'reconcile':
            True,
        })
        cls.asset_cat_sale = cls.asset_category.create({
            'name':
            'Sale category',
            'journal_id':
            cls.journal_sale.id,
            'account_asset_id':
            cls.account_sale.id,
            'account_depreciation_id':
            cls.account_sale.id,
            'account_depreciation_expense_id':
            cls.account_sale.id,
            'type':
            'sale',
            'method_number':
            2,
            'method_period':
            1,
        })
        cls.asset_cat_purchase = cls.asset_category.create({
            'name':
            'Purchase category',
            'journal_id':
            cls.journal_purchase.id,
            'account_asset_id':
            cls.account_purchase.id,
            'account_depreciation_id':
            cls.account_purchase.id,
            'account_depreciation_expense_id':
            cls.account_purchase.id,
            'type':
            'purchase',
            'method_number':
            2,
            'method_period':
            1,
        })

        cls.analytic_acc_1 = cls.aa_obj.create({
            "name": "Analytic acc 1",
        })
        cls.analytic_acc_2 = cls.aa_obj.create({
            "name": "Analytic acc 2",
        })

    def test_sale_asset_analytic_account(self):
        asset = self.asset.create({
            "name": "Sale Asset",
            "category_id": self.asset_cat_sale.id,
            "date": datetime.now().date(),
            "account_analytic_id": self.analytic_acc_1.id,
            "value": 777.77,
            "method_number": 2,
            "month_period": 1,
        })
        asset.validate()
        asset.depreciation_line_ids.create_grouped_move()
        move_id_1 = asset.depreciation_line_ids[0].move_id
        move_id_2 = asset.depreciation_line_ids[1].move_id
        self.assertEquals(asset.account_analytic_id,
                          move_id_1.line_ids[1].analytic_account_id)
        self.assertEquals(asset.account_analytic_id,
                          move_id_2.line_ids[1].analytic_account_id)

    def test_purchase_asset_analytic_account(self):
        asset = self.asset.create({
            "name": "Purchase Asset",
            "category_id": self.asset_cat_purchase.id,
            "date": datetime.now().date(),
            "account_analytic_id": self.analytic_acc_1.id,
            "value": 777.77,
            "method_number": 2,
            "month_period": 1,
        })
        asset.validate()
        asset.depreciation_line_ids.create_grouped_move()
        move_id_1 = asset.depreciation_line_ids[0].move_id
        move_id_2 = asset.depreciation_line_ids[1].move_id
        self.assertEquals(asset.account_analytic_id,
                          move_id_1.line_ids[0].analytic_account_id)
        self.assertEquals(asset.account_analytic_id,
                          move_id_2.line_ids[0].analytic_account_id)

    def test_onchange_category_id(self):
        self.asset_cat_sale.account_analytic_id = self.analytic_acc_2
        asset = self.asset.create({
            "name": "Onchange Asset",
            "category_id": self.asset_cat_purchase.id,
            "date": datetime.now().date(),
            "account_analytic_id": self.analytic_acc_1.id,
            "value": 777.77,
            "method_number": 2,
            "month_period": 1,
        })
        asset.category_id = self.asset_cat_sale
        asset.onchange_category_id()
        self.assertEquals(asset.account_analytic_id, self.analytic_acc_2)
