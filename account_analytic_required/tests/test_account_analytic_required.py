# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account analytic required module for OpenERP
#    Copyright (C) 2014 Acsone (http://acsone.eu). All Rights Reserved
#    @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime

from openerp.tests import common
from openerp.osv import orm


class test_account_analytic_required(common.TransactionCase):

    def setUp(self):
        super(test_account_analytic_required, self).setUp()
        self.account_obj = self.registry('account.account')
        self.account_type_obj = self.registry('account.account.type')
        self.move_obj = self.registry('account.move')
        self.move_line_obj = self.registry('account.move.line')
        self.analytic_account_obj = self.registry('account.analytic.account')
        self.analytic_account_id = self.analytic_account_obj.create(
            self.cr, self.uid, {'name': 'test aa', 'type': 'normal'})

    def _create_move(self, with_analytic, amount=100):
        date = datetime.now()
        period_id = self.registry('account.period').find(
            self.cr, self.uid, date,
            context={'account_period_prefer_normal': True})[0]
        move_vals = {
            'journal_id': self.ref('account.sales_journal'),
            'period_id': period_id,
            'date': date,
        }
        move_id = self.move_obj.create(self.cr, self.uid, move_vals)
        move_line_id = self.move_line_obj.create(
            self.cr, self.uid,
            {'move_id': move_id,
             'name': '/',
             'debit': 0,
             'credit': amount,
             'account_id': self.ref('account.a_sale'),
             'analytic_account_id':
             self.analytic_account_id if with_analytic else False})
        self.move_line_obj.create(
            self.cr, self.uid,
            {'move_id': move_id,
             'name': '/',
             'debit': amount,
             'credit': 0,
             'account_id': self.ref('account.a_recv')})
        return move_line_id

    def _set_analytic_policy(self, policy, aref='account.a_sale'):
        account_type = self.account_obj.browse(self.cr, self.uid,
                                               self.ref(aref)).user_type
        self.account_type_obj.write(self.cr, self.uid, account_type.id,
                                    {'analytic_policy': policy})

    def test_optional(self):
        self._create_move(with_analytic=False)
        self._create_move(with_analytic=True)

    def test_always_no_analytic(self):
        self._set_analytic_policy('always')
        with self.assertRaises(orm.except_orm):
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
        with self.assertRaises(orm.except_orm):
            self._create_move(with_analytic=True)

    def test_never_with_analytic_0(self):
        # accept analytic when debit=credit=0
        self._set_analytic_policy('never')
        self._create_move(with_analytic=True, amount=0)

    def test_always_remove_analytic(self):
        # remove partner when policy is always
        self._set_analytic_policy('always')
        line_id = self._create_move(with_analytic=True)
        with self.assertRaises(orm.except_orm):
            self.move_line_obj.write(self.cr, self.uid, [line_id],
                                     {'analytic_account_id': False})

    def test_change_account(self):
        self._set_analytic_policy('always', aref='account.a_expense')
        line_id = self._create_move(with_analytic=False)
        # change account to a_expense with policy always but missing
        # analytic_account
        with self.assertRaises(orm.except_orm):
            self.move_line_obj.write(
                self.cr, self.uid, [line_id],
                {'account_id': self.ref('account.a_expense')})
        # change account to a_expense with policy always
        # with analytic account -> ok
        self.move_line_obj.write(
            self.cr, self.uid, [line_id], {
                'account_id': self.ref('account.a_expense'),
                'analytic_account_id': self.analytic_account_id})
