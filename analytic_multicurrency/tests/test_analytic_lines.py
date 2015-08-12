# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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

import time
from openerp.tests import common


class testAnalyticLine(common.TransactionCase):

    def setUp(self):
        super(testAnalyticLine, self).setUp()
        self.agrolait = self.ref('account.analytic_agrolait')
        self.expense = self.ref('account.income_fx_expense')

        self.account_analytic_line_obj = self.registry('account.analytic.line')
        self.account_analytic_account_obj = (
            self.registry('account.analytic.account')
        )
        self.res_currency_rate_model = self.registry('res.currency.rate')
        model_data_obj = self.registry("ir.model.data")
        self.main_company = model_data_obj.get_object_reference(
            self.cr, self.uid, "base", "main_company")[1]
        self.partner_agrolait_id = model_data_obj.get_object_reference(
            self.cr, self.uid, "base", "res_partner_2")[1]
        self.currency_eur_id = model_data_obj.get_object_reference(
            self.cr, self.uid, "base", "EUR")[1]
        self.currency_usd_id = model_data_obj.get_object_reference(
            self.cr, self.uid, "base", "USD")[1]
        self.account_rcv_id = model_data_obj.get_object_reference(
            self.cr, self.uid, "account", "a_recv")[1]

        self.account_fx_income_id = model_data_obj.get_object_reference(
            self.cr, self.uid, "account", "income_fx_income")[1]
        self.account_fx_expense_id = model_data_obj.get_object_reference(
            self.cr, self.uid, "account", "income_fx_expense")[1]

        self.product_id = model_data_obj.get_object_reference(
            self.cr, self.uid, "product", "product_product_4")[1]

        self.acs_model = self.registry('account.config.settings')

        acs_ids = self.acs_model.search(
            self.cr, self.uid,
            [('company_id', '=', self.ref("base.main_company"))]
            )

        values = {'group_multi_currency': True,
                  'income_currency_exchange_account_id':
                  self.account_fx_income_id,
                  'expense_currency_exchange_account_id':
                  self.account_fx_expense_id}

        if acs_ids:
            self.acs_model.write(self.cr, self.uid, acs_ids, values)
        else:
            default_vals = self.acs_model.default_get(self.cr, self.uid, [])
            default_vals.update(values)
            default_vals['date_stop'] = time.strftime('%Y-12-31')
            default_vals['date_start'] = time.strftime('%Y-%m-%d')
            default_vals['period'] = 'month'
            self.acs_model.create(self.cr, self.uid, default_vals)

        self.aajournal = self.ref('account.analytic_journal_sale')

    def test_analytic_lines(self):
        cr, uid = self.cr, self.uid

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual('EUR', aal_brw.aa_currency_id.name)
        self.assertEqual(100, aal_brw.aa_amount_currency)
        self.assertEqual(100, aal_brw.account_id.ca_invoiced)
        self.assertEqual(0, aal_brw.account_id.total_cost)

    def test_analytic_lines2(self):
        cr, uid = self.cr, self.uid
        self.res_currency_rate_model.create(cr, uid, {
            'name': time.strftime('%Y-%m-%d') + ' 00:00:00',
            'currency_id': self.currency_usd_id,
            'rate': 0.50,
        })
        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_usd_id}
        )
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual('USD', aal_brw.aa_currency_id.name)
        self.assertEqual(50, aal_brw.aa_amount_currency)

    def test_analytic_lines3(self):
        cr, uid = self.cr, self.uid
        self.res_currency_rate_model.create(cr, uid, {
            'name': time.strftime('%Y-%m-%d') + ' 00:00:00',
            'currency_id': self.currency_usd_id,
            'rate': 0.50,
        })

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual('EUR', aal_brw.aa_currency_id.name)
        self.assertEqual(100, aal_brw.aa_amount_currency)

        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_usd_id}
        )
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual('USD', aal_brw.aa_currency_id.name)
        self.assertEqual(50, aal_brw.aa_amount_currency)

    def test_analytic_lines4(self):
        cr, uid = self.cr, self.uid
        self.res_currency_rate_model.create(cr, uid, {
            'name': time.strftime('%Y-%m-%d') + ' 00:00:00',
            'currency_id': self.currency_usd_id,
            'rate': 0.50,
        })
        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_usd_id}
        )
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(50, aal_brw.account_id.debit)
        self.assertEqual(50, aal_brw.account_id.balance)

    def test_analytic_lines5(self):
        cr, uid = self.cr, self.uid
        self.res_currency_rate_model.create(cr, uid, {
            'name': time.strftime('%Y-%m-%d') + ' 00:00:00',
            'currency_id': self.currency_usd_id,
            'rate': 0.50,
        })
        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_usd_id}
        )
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(50, aal_brw.account_id.debit)
        self.assertEqual(50, aal_brw.account_id.balance)

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': -200,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(100, aal_brw.account_id.credit)
        self.assertEqual(50, aal_brw.account_id.debit)
        self.assertEqual(-50, aal_brw.account_id.balance)

        self.assertEqual(-50, aal_brw.account_id.ca_invoiced)
        self.assertEqual(-100, aal_brw.account_id.total_cost)

    def test_analytic_lines6(self):
        cr, uid = self.cr, self.uid
        self.res_currency_rate_model.create(cr, uid, {
            'name': time.strftime('%Y-%m-%d') + ' 00:00:00',
            'currency_id': self.currency_usd_id,
            'rate': 0.50,
        })
        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_usd_id}
        )
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(50, aal_brw.account_id.debit)
        self.assertEqual(50, aal_brw.account_id.balance)

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': -200,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(100, aal_brw.account_id.credit)
        self.assertEqual(50, aal_brw.account_id.debit)
        self.assertEqual(-50, aal_brw.account_id.balance)

        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_eur_id}
        )
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(200, aal_brw.account_id.credit)
        self.assertEqual(100, aal_brw.account_id.debit)
        self.assertEqual(-100, aal_brw.account_id.balance)

    def test_analytic_lines7(self):
        cr, uid = self.cr, self.uid
        self.res_currency_rate_model.create(cr, uid, {
            'name': time.strftime('%Y-%m-%d') + ' 00:00:00',
            'currency_id': self.currency_usd_id,
            'rate': 0.50,
        })
        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_usd_id}
        )
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(50, aal_brw.account_id.debit)
        self.assertEqual(50, aal_brw.account_id.balance)

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': -200,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(100, aal_brw.account_id.credit)
        self.assertEqual(50, aal_brw.account_id.debit)
        self.assertEqual(-50, aal_brw.account_id.balance)

        self.registry('account.analytic.account').write(
            cr, uid,
            [self.agrolait],
            {'currency_id': self.currency_eur_id}
        )
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(200, aal_brw.account_id.credit)
        self.assertEqual(100, aal_brw.account_id.debit)
        self.assertEqual(-100, aal_brw.account_id.balance)

    def test_analytic_lines8(self):
        cr, uid = self.cr, self.uid

        new_aaa_id = self.registry('account.analytic.account').create(
            cr, uid,
            {'name': 'TEST currency'}
        )
        analytic_brw = self.account_analytic_account_obj.browse(
            cr,
            uid,
            new_aaa_id,
            )
        self.assertEqual(self.currency_eur_id,
                         analytic_brw.currency_id.id)
        self.registry('res.company').write(
            cr, uid, self.main_company,
            {'currency_id': self.currency_usd_id}
            )
        analytic_brw.refresh()
        self.assertEqual(self.currency_usd_id,
                         analytic_brw.currency_id.id)

    def test_analytic_lines9(self):
        cr, uid = self.cr, self.uid
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-01'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(100, aal_brw.account_id.debit)
        self.assertEqual(100, aal_brw.account_id.balance)

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': -200,
            'general_account_id': self.account_rcv_id,
        })
        ctx = {'from_date': time.strftime('%Y-%m-%d')}
        aal_brw = self.account_analytic_line_obj.browse(cr, uid,
                                                        aal_id, context=ctx)
        self.assertEqual(200, aal_brw.account_id.credit)
        self.assertEqual(0, aal_brw.account_id.debit)
        self.assertEqual(-200, aal_brw.account_id.balance)

    def test_analytic_lines10(self):
        cr, uid = self.cr, self.uid
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-01'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(100, aal_brw.account_id.debit)
        self.assertEqual(100, aal_brw.account_id.balance)

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': -200,
            'general_account_id': self.account_rcv_id,
        })

        ctx = {'to_date': time.strftime('%Y-%m-01')}
        aal_brw = self.account_analytic_line_obj.browse(cr, uid,
                                                        aal_id, context=ctx)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(100, aal_brw.account_id.debit)
        self.assertEqual(100, aal_brw.account_id.balance)

    def test_analytic_lines11(self):
        cr, uid = self.cr, self.uid
        self.res_currency_rate_model.create(cr, uid, {
            'name': time.strftime('%Y-%m-%d') + ' 00:00:00',
            'currency_id': self.currency_usd_id,
            'rate': 0.50,
        })
        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-01'),
            'amount': 100,
            'general_account_id': self.account_rcv_id,
        })
        aal_brw = self.account_analytic_line_obj.browse(cr, uid, aal_id)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(100, aal_brw.account_id.debit)
        self.assertEqual(100, aal_brw.account_id.balance)

        aal_id = self.account_analytic_line_obj.create(cr, uid, {
            'account_id': self.agrolait,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal,
            'date': time.strftime('%Y-%m-%d'),
            'amount': -200,
            'general_account_id': self.account_rcv_id,
        })
        ctx = {'from_date': time.strftime('%Y-%m-%d')}
        aal_brw = self.account_analytic_line_obj.browse(cr, uid,
                                                        aal_id, context=ctx)
        self.assertEqual(200, aal_brw.account_id.credit)
        self.assertEqual(0, aal_brw.account_id.debit)
        self.assertEqual(-200, aal_brw.account_id.balance)

        ctx = {'to_date': time.strftime('%Y-%m-01')}
        aal_brw = self.account_analytic_line_obj.browse(cr, uid,
                                                        aal_id, context=ctx)
        self.assertEqual(0, aal_brw.account_id.credit)
        self.assertEqual(100, aal_brw.account_id.debit)
        self.assertEqual(100, aal_brw.account_id.balance)
