# -*- coding: utf-8 -*-
# © 2014 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from odoo.tests import common
from odoo import exceptions


class TestAccountAnalyticRequired(common.TransactionCase):

    def setUp(self):
        super(TestAccountAnalyticRequired, self).setUp()
        self.account_obj = self.env['account.account']
        self.account_type_obj = self.env['account.account.type']
        self.move_obj = self.env['account.move']
        self.move_line_obj = self.env['account.move.line']
        self.analytic_account_obj = self.env['account.analytic.account']
        self.analytic_account = self.analytic_account_obj.create(
            {'name': 'test aa'})
        self.account_sales = self.env['account.account'].create({
            'code': "X1020",
            'name': "Product Sales - (test)",
            'user_type_id': self.ref('account.data_account_type_revenue')
        })
        self.account_recv = self.env['account.account'].create({
            'code': "X11002",
            'name': "Debtors - (test)",
            'reconcile': True,
            'user_type_id': self.ref('account.data_account_type_receivable')
        })
        self.account_exp = self.env['account.account'].create({
            'code': "X2110",
            'name': "Expenses - (test)",
            'user_type_id': self.ref('account.data_account_type_expenses')
        })
        self.sales_journal = self.env['account.journal'].create({
            'name': "Sales Journal - (test)",
            'code': "TSAJ",
            'type': "sale",
            'refund_sequence': True,
            'default_debit_account_id': self.account_sales.id,
            'default_credit_account_id': self.account_sales.id,
        })

    def _create_move(self, with_analytic, amount=100):
        date = datetime.now()
        ml_obj = self.move_line_obj.with_context(check_move_validity=False)
        move_vals = {
            'name': '/',
            'journal_id': self.sales_journal.id,
            'date': date,
        }
        move = self.move_obj.create(move_vals)
        move_line = ml_obj.create(
            {'move_id': move.id,
             'name': '/',
             'debit': 0,
             'credit': amount,
             'account_id': self.account_sales.id,
             'analytic_account_id':
             self.analytic_account.id if with_analytic else False})
        ml_obj.create(
            {'move_id': move.id,
             'name': '/',
             'debit': amount,
             'credit': 0,
             'account_id': self.account_recv.id,
             })
        return move_line

    def _set_analytic_policy(self, policy, account=None):
        if account is None:
            account = self.account_sales
        account.user_type_id.analytic_policy = policy

    def test_optional(self):
        self._set_analytic_policy('optional')
        self._create_move(with_analytic=False)
        self._create_move(with_analytic=True)

    def test_always_no_analytic(self):
        self._set_analytic_policy('always')
        with self.assertRaises(exceptions.ValidationError):
            self._create_move(with_analytic=False)

    def test_always_no_analytic_0(self):
        # accept missing analytic account when debit=credit=0
        self._set_analytic_policy('always')
        self._create_move(with_analytic=False, amount=0)

    def test_always_with_analytic(self):
        self._set_analytic_policy('always')
        self._create_move(with_analytic=True)

    def test_never_no_analytic(self):
        self._set_analytic_policy('never')
        self._create_move(with_analytic=False)

    def test_never_with_analytic(self):
        self._set_analytic_policy('never')
        with self.assertRaises(exceptions.ValidationError):
            self._create_move(with_analytic=True)

    def test_never_with_analytic_0(self):
        # accept analytic when debit=credit=0
        self._set_analytic_policy('never')
        self._create_move(with_analytic=True, amount=0)

    def test_always_remove_analytic(self):
        # remove analytic when policy is always
        self._set_analytic_policy('always')
        line = self._create_move(with_analytic=True)
        with self.assertRaises(exceptions.ValidationError):
            line.write({'analytic_account_id': False})

    def test_change_account(self):
        self._set_analytic_policy('always', account=self.account_exp)
        line = self._create_move(with_analytic=False)
        # change account to a_expense with policy always but missing
        # analytic_account
        with self.assertRaises(exceptions.ValidationError):
            line.write({'account_id': self.account_exp.id})
        # change account to a_expense with policy always
        # with analytic account -> ok
        line.write({
            'account_id': self.account_exp.id,
            'analytic_account_id': self.analytic_account.id})
