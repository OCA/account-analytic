# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import common


class TestAnalyticCurrency(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.AccountAnalyticAccount = self.env['account.analytic.account']
        self.eur = self.env.ref('base.EUR')

    def test_defaults(self):
        account = self.AccountAnalyticAccount.create({
            'name': 'Account',
        })

        self.assertEqual(account.currency_id, account.company_id.currency_id)

    def test_specific(self):
        account = self.AccountAnalyticAccount.create({
            'name': 'Account',
            'currency_id': self.eur.id,
        })

        self.assertEqual(account.currency_id, self.eur)

    def test_computation(self):
        account_usd = self.AccountAnalyticAccount.create({
            'name': 'Account USD',
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
        account_eur = self.AccountAnalyticAccount.create({
            'name': 'Account',
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
        })
        self.assertEqual(account_usd.credit, 150.0)
        self.assertEqual(account_usd.original_credit, 150.0)
        self.assertEqual(account_usd.debit, 50.0)
        self.assertEqual(account_usd.original_debit, 50.0)
        self.assertEqual(account_usd.balance, 100.0)
        self.assertEqual(account_usd.original_balance, 100.0)
        self.assertEqual(account_eur.credit, 192.51)
        self.assertEqual(account_eur.original_credit, 150.0)
        self.assertEqual(account_eur.debit, 64.17)
        self.assertEqual(account_eur.original_debit, 50.0)
        self.assertEqual(account_eur.balance, 128.34)
        self.assertEqual(account_eur.original_balance, 100.0)

    def test_safeguard(self):
        account = self.AccountAnalyticAccount.create({
            'name': 'Account',
            'line_ids': [
                (0, 0, {
                    'name': 'line',
                    'amount': 100.0,
                }),
            ],
        })
        with self.assertRaises(UserError):
            account.currency_id = self.eur

    def test_line(self):
        account = self.AccountAnalyticAccount.create({
            'name': 'Account',
            'line_ids': [
                (0, 0, {
                    'name': 'Line',
                    'amount': 50.0,
                }),
            ],
        })
        self.assertEqual(account.line_ids[0].user_amount, 50.0)
