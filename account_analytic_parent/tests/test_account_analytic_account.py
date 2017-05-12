# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestAccountAnalyticRecursion(TransactionCase):

    def setUp(self):
        super(TestAccountAnalyticRecursion, self).setUp()

        self.analytic_account_obj = self.env['account.analytic.account']
        self.analytic_line_obj = self.env['account.analytic.line']
        self.partner1 = self.env.ref('base.res_partner_1')
        self.partner2 = self.env.ref('base.res_partner_2')
        self.analytic_parent1 = self.analytic_account_obj.create(
            {'name': 'parent aa',
             'code': '01',
             'partner_id': self.partner1.id})
        self.analytic_son = self.analytic_account_obj.create(
            {'name': 'son aa',
             'code': '02',
             'parent_id': self.analytic_parent1.id})
        self.analytic_parent2 = self.analytic_account_obj.create(
            {'name': 'parent2 aa',
             'code': '01',
             'partner_id': self.partner2.id})
        self.create_analytic_line(
            'Analytic line son', self.analytic_son, 50)
        self.create_analytic_line(
            'Analytic line parent1', self.analytic_parent1, 100)
        self.create_analytic_line(
            'Analytic line parent2', self.analytic_parent2, 50)
        self.assertEqual(self.analytic_parent1.debit, 0,
                         'Analytic account in the debit side')

    def create_analytic_line(self, name, analytic, amount):
        return self.analytic_line_obj.create({
            'name': name,
            'amount': amount,
            'account_id': analytic.id})

    def test_recursion(self):
        with self.assertRaises(ValidationError):
            self.analytic_parent1.write(
                {'parent_id': self.analytic_son.id})

    def test_onchange(self):
        self.analytic_son.on_change_parent()
        self.assertEqual(self.analytic_son.partner_id.id, self.partner1.id,
                         'Partner should not change')
        self.analytic_son.write({'parent_id': self.analytic_parent2.id})
        self.analytic_son.on_change_parent()
        self.assertEqual(self.analytic_son.partner_id.id, self.partner2.id,
                         'Partner should change')

    def test_debit_credit_balance(self):
        self.assertEqual(self.analytic_parent1.credit, 150, 'Wrong amount')
        self.assertEqual(self.analytic_parent1.balance, 150, 'Wrong amount')
        self.assertEqual(self.analytic_son.debit, 0,
                         'Analytic account in the debit side')
        self.assertEqual(self.analytic_son.credit, 50, 'Wrong amount')
        self.assertEqual(self.analytic_son.balance, 50, 'Wrong amount')
        self.assertEqual(self.analytic_parent2.debit, 0,
                         'Analytic account in the debit side')
        self.assertEqual(self.analytic_parent2.credit, 50, 'Wrong amount')
        self.assertEqual(self.analytic_parent2.balance, 50, 'Wrong amount')

    def test_wizard(self):
        self.wizard = self.env['account.analytic.chart'].create({
            'from_date': '2017-01-01',
            'to_date': '2017-12-31',
        })
        result = self.wizard.analytic_account_chart_open_window()
        self.assertTrue('2017-01-01' in result['context'])
        self.assertTrue('2017-12-31' in result['context'])
