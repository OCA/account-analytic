# -*- coding: utf-8 -*-
# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAnalyticDimensionCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestAnalyticDimensionCase, self).setUp(*args, **kwargs)

        self.dimension_obj = self.env['account.analytic.dimension']
        self.tag_obj = self.env['account.analytic.tag']
        self.analytic_line_obj = self.env['account.analytic.line']
        self.account_obj = self.env['account.account']

        self.analytic_dimension_type = self.env.ref(
            'analytic_tag_dimension.analytic_dimension_type')
        self.analytic_dimension_concept = self.env.ref(
            'analytic_tag_dimension.analytic_dimension_concept')
        self.analytic_tag_type_a = self.env.ref(
            'analytic_tag_dimension.analytic_tag_type_a')
        self.analytic_tag_type_b = self.env.ref(
            'analytic_tag_dimension.analytic_tag_type_b')
        self.analytic_tag_concept_a = self.env.ref(
            'analytic_tag_dimension.analytic_tag_concept_a')
        self.analytic_tag_concept_b = self.env.ref(
            'analytic_tag_dimension.analytic_tag_concept_b')

        self.analytic_account_id = self.env.ref(
            'analytic.analytic_absences').id

        self.account_user_type = self.env.ref(
            'account.data_account_type_receivable')
        self.journal = self.env['account.journal'].search([], limit=1)

        self.company_id = self.env['res.users'].browse(
            self.env.uid).company_id.id

    def test_analytic_entry_dimension(self):
        """Test dimension creation on analytic entry creation
        """
        analytic_dimension_test = self.dimension_obj.create({
            'name': 'Test_creation',
            'code': 'test'
        })
        analytic_tag_test_a = self.tag_obj.create({
            'name': 'Test A',
            'analytic_dimension_id': analytic_dimension_test.id
        })
        values = {
            'account_id': self.analytic_account_id,
            'name': 'test',
            'tag_ids': [(6, 0, [self.analytic_tag_type_a.id,
                                self.analytic_tag_concept_a.id,
                                analytic_tag_test_a.id])]
        }
        line = self.analytic_line_obj.create(values)
        self.assertTrue(
            line.x_dimension_type.id == self.analytic_tag_type_a.id)
        self.assertTrue(
            line.x_dimension_concept.id == self.analytic_tag_concept_a.id)
        values_update = {
            'tag_ids': [(6, 0, [self.analytic_tag_type_a.id,
                                self.analytic_tag_type_b.id])]
        }
        with self.assertRaises(ValidationError):
            line.write(values_update)

    def test_account_entry_dimension(self):
        """Test dimension creation on account move line creation
        """

        account = self.account_obj.create({
            'code': 'test_dimension_acc_01',
            'name': 'test dimension account',
            'user_type_id': self.account_user_type.id,
            'reconcile': True,
        })
        self.move = self.env['account.move'].create({
            'name': '/',
            'ref': '2011010',
            'journal_id': self.journal.id,
            'state': 'draft',
            'company_id': self.company_id,
        })
        values = {
            'name': 'test',
            'account_id': account.id,
            'move_id': self.move.id,
            'analytic_account_id': self.analytic_account_id,
            'analytic_tag_ids': [(6, 0, [self.analytic_tag_type_a.id,
                                         self.analytic_tag_concept_a.id])]
        }
        move_line_obj = self.env['account.move.line']
        line = move_line_obj.create(values)
        self.assertTrue(
            line.x_dimension_type.id == self.analytic_tag_type_a.id)
        self.assertTrue(
            line.x_dimension_concept.id == self.analytic_tag_concept_a.id)
        values_update = {
            'analytic_tag_ids': [(6, 0, [self.analytic_tag_type_a.id,
                                         self.analytic_tag_type_b.id])]
        }
        with self.assertRaises(ValidationError):
            line.write(values_update)

    def test_invoice_line_dimension(self):
        """Test dimension creation on account invoice line creation
        """
        partner = self.env.ref('base.res_partner_2')
        account = self.account_obj.create({
            'code': 'test_dimension_acc_02',
            'name': 'test dimension account',
            'user_type_id': self.account_user_type.id,
            'reconcile': True,
        })
        self.invoice = self.env['account.invoice'].create({
            'journal_id': self.journal.id,
            'company_id': self.company_id,
            'partner_id': partner.id
        })
        values = {
            'name': 'test',
            'price_unit': 1,
            'account_id': account.id,
            'invoice_id': self.invoice.id,
            'analytic_account_id': self.analytic_account_id,
            'analytic_tag_ids': [(6, 0, [self.analytic_tag_type_a.id,
                                         self.analytic_tag_concept_a.id])]
        }
        invoice_line_obj = self.env['account.invoice.line']
        line = invoice_line_obj.create(values)
        self.assertTrue(
            line.x_dimension_type.id == self.analytic_tag_type_a.id)
        self.assertTrue(
            line.x_dimension_concept.id == self.analytic_tag_concept_a.id)
        values_update = {
            'analytic_tag_ids': [(6, 0, [self.analytic_tag_type_a.id])]
        }
        line.write(values_update)
        values_update = {
            'analytic_tag_ids': [(6, 0, [self.analytic_tag_type_a.id,
                                         self.analytic_tag_type_b.id])]
        }
        with self.assertRaises(ValidationError):
            line.write(values_update)
