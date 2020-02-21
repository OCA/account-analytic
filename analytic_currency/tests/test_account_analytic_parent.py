# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestAccountAnalyticParent(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.AccountAnalyticAccount = self.env['account.analytic.account']
        self.eur = self.env.ref('base.EUR')

    def test_parent_child(self):
        if not self.AccountAnalyticAccount._parent_store:
            return

        parent_account = self.AccountAnalyticAccount.create({
            'name': 'Parent Account',
            'line_ids': [
                (0, 0, {
                    'name': 'USD line 1',
                    'amount': 50.0,
                }),
                (0, 0, {
                    'name': 'USD line 2',
                    'amount': 50.0,
                }),
                (0, 0, {
                    'name': 'USD line 3',
                    'amount': -50.0,
                }),
                (0, 0, {
                    'name': 'USD line 4',
                    'amount': 50.0,
                }),
            ],
        })
        child_account = self.AccountAnalyticAccount.create({
            'name': 'Child Account',
            'currency_id': self.eur.id,
            'line_ids': [
                (0, 0, {
                    'name': 'EUR line 1',
                    'amount': 50.0,
                }),
                (0, 0, {
                    'name': 'EUR line 2',
                    'amount': 50.0,
                }),
                (0, 0, {
                    'name': 'EUR line 3',
                    'amount': -50.0,
                }),
                (0, 0, {
                    'name': 'EUR line 4',
                    'amount': 50.0,
                }),
            ],
            self.AccountAnalyticAccount._parent_name: parent_account.id,
        })
        self.assertEqual(parent_account.credit, 342.51)
        self.assertEqual(parent_account.original_credit, 342.51)
        self.assertEqual(parent_account.debit, 114.17)
        self.assertEqual(parent_account.original_debit, 114.17)
        self.assertEqual(parent_account.balance, 228.34)
        self.assertEqual(parent_account.original_balance, 228.34)
        self.assertEqual(child_account.credit, 192.51)
        self.assertEqual(child_account.original_credit, 150.0)
        self.assertEqual(child_account.debit, 64.17)
        self.assertEqual(child_account.original_debit, 50.0)
        self.assertEqual(child_account.balance, 128.34)
        self.assertEqual(child_account.original_balance, 100.0)
