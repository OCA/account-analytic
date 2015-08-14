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

from openerp import fields
from openerp.tests import common


class TestAnalyticLine(common.TransactionCase):

    def setUp(self):
        super(TestAnalyticLine, self).setUp()
        self.agrolait = self.env.ref('account.analytic_agrolait')
        self.expense = self.env.ref('account.income_fx_expense')

        self.account_analytic_line_obj = self.env['account.analytic.line']
        self.account_analytic_account_obj = (
            self.env['account.analytic.account']
        )
        self.res_currency_rate_model = self.env['res.currency.rate']
        self.main_company = self.env.ref("base.main_company")
        self.partner_agrolait_id = self.env.ref("base.res_partner_2")
        self.currency_eur_id = self.env.ref("base.EUR")
        self.currency_usd_id = self.env.ref("base.USD")
        self.account_rcv_id = self.env.ref("account.a_recv")

        self.account_fx_income_id = self.env.ref("account.income_fx_income")
        self.account_fx_expense_id = (
            self.env.ref("account.income_fx_expense")
            )
        self.product_id = self.env.ref("product.product_product_4")

        self.acs_model = self.env['account.config.settings']

        acs_rs = self.acs_model.search(
            [('company_id', '=', self.main_company.id)]
            )

        values = {'group_multi_currency': True,
                  'income_currency_exchange_account_id':
                  self.account_fx_income_id.id,
                  'expense_currency_exchange_account_id':
                  self.account_fx_expense_id.id}

        if acs_rs:
            acs_rs.write(values)
        else:
            default_vals = {}
            default_vals.update(values)
            default_vals['date_stop'] = fields.Date.to_string(
                fields.Date.from_string(
                    fields.Date.today()
                    ).replace(month=12, day=31))
            default_vals['date_start'] = fields.Date.today()
            default_vals['period'] = 'month'
            self.acs_model.create(default_vals)

        self.aajournal = self.env.ref('account.analytic_journal_sale')

    def test_amount_currency_no_currency_rate(self):
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertEqual('EUR', aal_rs.aa_currency_id.name)
        self.assertAlmostEqual(100, aal_rs.aa_amount_currency)
        self.assertAlmostEqual(100, aal_rs.account_id.ca_invoiced)
        self.assertAlmostEqual(0, aal_rs.account_id.total_cost)

    def test_amount_currency_with_currency_rate(self):
        self.res_currency_rate_model.create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.currency_usd_id.id,
            'rate': 0.50,
        })
        self.agrolait.write(
            {'currency_id': self.currency_usd_id.id}
        )
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertEqual('USD', aal_rs.aa_currency_id.name)
        self.assertAlmostEqual(50, aal_rs.aa_amount_currency)

    def test_amount_with_currency_rate_and_double_currency_change(self):
        self.res_currency_rate_model.create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.currency_usd_id.id,
            'rate': 0.50,
        })

        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertEqual('EUR', aal_rs.aa_currency_id.name)
        self.assertAlmostEqual(100, aal_rs.aa_amount_currency)

        self.agrolait.write(
            {'currency_id': self.currency_usd_id.id}
        )
        self.assertEqual('USD', aal_rs.aa_currency_id.name)
        self.assertAlmostEqual(50, aal_rs.aa_amount_currency)

    def test_amount_currency_with_currency_rate_and_currency_change(self):
        self.res_currency_rate_model.create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.currency_usd_id.id,
            'rate': 0.50,
        })
        self.agrolait.write(
            {'currency_id': self.currency_usd_id.id}
        )
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(0, aal_rs.account_id.credit)
        self.assertAlmostEqual(50, aal_rs.account_id.debit)
        self.assertAlmostEqual(50, aal_rs.account_id.balance)

    def test_amount_ca_total_cost_with_currency_rate_and_currency_change(self):
        self.res_currency_rate_model.create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.currency_usd_id.id,
            'rate': 0.50,
        })
        self.agrolait.write(
            {'currency_id': self.currency_usd_id.id}
        )
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(0, aal_rs.account_id.credit)
        self.assertAlmostEqual(50, aal_rs.account_id.debit)
        self.assertAlmostEqual(50, aal_rs.account_id.balance)

        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': -200,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(100, aal_rs.account_id.credit)
        self.assertAlmostEqual(50, aal_rs.account_id.debit)
        self.assertAlmostEqual(-50, aal_rs.account_id.balance)

        self.assertAlmostEqual(-50, aal_rs.account_id.ca_invoiced)
        self.assertAlmostEqual(-100, aal_rs.account_id.total_cost)

    def test_amount_with_currency_rate_and_currency_change_2_lines(self):
        self.res_currency_rate_model.create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.currency_usd_id.id,
            'rate': 0.50,
        })
        self.agrolait.write(
            {'currency_id': self.currency_usd_id.id}
        )
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(0, aal_rs.account_id.credit)
        self.assertAlmostEqual(50, aal_rs.account_id.debit)
        self.assertAlmostEqual(50, aal_rs.account_id.balance)

        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': -200,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(100, aal_rs.account_id.credit)
        self.assertAlmostEqual(50, aal_rs.account_id.debit)
        self.assertAlmostEqual(-50, aal_rs.account_id.balance)

        self.agrolait.write(
            {'currency_id': self.currency_eur_id.id}
        )
        self.assertAlmostEqual(200, aal_rs.account_id.credit)
        self.assertAlmostEqual(100, aal_rs.account_id.debit)
        self.assertAlmostEqual(-100, aal_rs.account_id.balance)

    def test_amount_with_currency_rate_and_dbl_currency_change_2_lines(self):
        self.res_currency_rate_model.create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.currency_usd_id.id,
            'rate': 0.50,
        })
        self.agrolait.write(
            {'currency_id': self.currency_usd_id.id}
        )
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(0, aal_rs.account_id.credit)
        self.assertAlmostEqual(50, aal_rs.account_id.debit)
        self.assertAlmostEqual(50, aal_rs.account_id.balance)

        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': -200,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(100, aal_rs.account_id.credit)
        self.assertAlmostEqual(50, aal_rs.account_id.debit)
        self.assertAlmostEqual(-50, aal_rs.account_id.balance)

        self.agrolait.write(
            {'currency_id': self.currency_eur_id.id}
        )
        self.assertAlmostEqual(200, aal_rs.account_id.credit)
        self.assertAlmostEqual(100, aal_rs.account_id.debit)
        self.assertAlmostEqual(-100, aal_rs.account_id.balance)

    def test_account_currency_change_company_currency(self):
        new_aaa_rs = self.env['account.analytic.account'].create(
            {'name': 'TEST currency'}
        )
        self.assertEqual(self.currency_eur_id.id,
                         new_aaa_rs.currency_id.id)
        self.main_company.write(
            {'currency_id': self.currency_usd_id.id}
            )
        self.assertEqual(self.currency_usd_id.id,
                         new_aaa_rs.currency_id.id)

    def test_amount_with_context_from_date(self):
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.to_string(fields.Date.from_string(
                fields.Date.today()
                ).replace(day=1)),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(0, aal_rs.account_id.credit)
        self.assertAlmostEqual(100, aal_rs.account_id.debit)
        self.assertAlmostEqual(100, aal_rs.account_id.balance)

        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': -200,
            'general_account_id': self.account_rcv_id.id,
        })
        aal2 = aal_rs.with_context(from_date=fields.Date.today())
        self.assertAlmostEqual(200, aal2.account_id.credit)
        self.assertAlmostEqual(0, aal2.account_id.debit)
        self.assertAlmostEqual(-200, aal2.account_id.balance)

    def test_amount_with_context_date_to(self):
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.to_string(fields.Date.from_string(
                fields.Date.today()
                ).replace(day=1)),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(0, aal_rs.account_id.credit)
        self.assertAlmostEqual(100, aal_rs.account_id.debit)
        self.assertAlmostEqual(100, aal_rs.account_id.balance)

        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': -200,
            'general_account_id': self.account_rcv_id.id,
        })
        todate = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()
            ).replace(day=1))
        aal2 = aal_rs.with_context(to_date=todate)
        self.assertAlmostEqual(0, aal2.account_id.credit)
        self.assertAlmostEqual(100, aal2.account_id.debit)
        self.assertAlmostEqual(100, aal2.account_id.balance)

    def test_amount_with_context_from_date_date_to(self):
        self.res_currency_rate_model.create({
            'name': fields.Date.today() + ' 00:00:00',
            'currency_id': self.currency_usd_id.id,
            'rate': 0.50,
        })
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.to_string(fields.Date.from_string(
                fields.Date.today()
                ).replace(day=1)),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
        })
        self.assertAlmostEqual(0, aal_rs.account_id.credit)
        self.assertAlmostEqual(100, aal_rs.account_id.debit)
        self.assertAlmostEqual(100, aal_rs.account_id.balance)

        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.today(),
            'amount': -200,
            'general_account_id': self.account_rcv_id.id,
        })
        aal2 = aal_rs.with_context(from_date=fields.Date.today())
        self.assertAlmostEqual(200, aal2.account_id.credit)
        self.assertAlmostEqual(0, aal2.account_id.debit)
        self.assertAlmostEqual(-200, aal2.account_id.balance)

        todate = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()
            ).replace(day=1))
        aal3 = aal_rs.with_context(to_date=todate)
        self.assertAlmostEqual(0, aal3.account_id.credit)
        self.assertAlmostEqual(100, aal3.account_id.debit)
        self.assertAlmostEqual(100, aal3.account_id.balance)

    def test_amount_on_change_unit_amount(self):
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.to_string(fields.Date.from_string(
                fields.Date.today()
                ).replace(day=1)),
            'amount': 100,
            'general_account_id': self.account_rcv_id.id,
            'product_id': self.product_id.id,
            'unit_amount': 2.0,
        })
        res = aal_rs.on_change_unit_amount(self.product_id.id, 2.0,
                                           self.main_company.id)
        self.assertAlmostEqual(-1000, res['value']['amount'])
        res = aal_rs.on_change_unit_amount(self.product_id.id, 4.0,
                                           self.main_company.id)
        self.assertAlmostEqual(-2000, res['value']['amount'])

    def test_amount_zero(self):
        aal_rs = self.account_analytic_line_obj.create({
            'account_id': self.agrolait.id,
            'name': 'AGROLAIT',
            'journal_id': self.aajournal.id,
            'date': fields.Date.to_string(fields.Date.from_string(
                fields.Date.today()
                ).replace(day=1)),
            'general_account_id': self.account_rcv_id.id,
        })
        aal_rs.account_id.write(
            {'currency_id': self.currency_usd_id.id}
        )
        self.assertAlmostEqual(0, aal_rs.amount)

    def test_account_check_recursion(self):
        self.assertTrue(self.agrolait.check_recursion())

    def test_account_change_currency(self):
        self.agrolait.write({'currency_id': False})
        self.assertEqual(self.currency_eur_id.id, self.agrolait.currency_id.id)
