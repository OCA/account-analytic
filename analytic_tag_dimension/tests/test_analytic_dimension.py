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

        self.analytic_dimension_test = self.dimension_obj.create({
            'name': 'Test_creation',
            'code': 'test'
        })
        self.analytic_tag_test_a = self.tag_obj.create({
            'name': 'Test A',
            'analytic_dimension_id': self.analytic_dimension_test.id
        })

        self.analytic_account_id = self.env.ref(
            'analytic.analytic_absences').id

    def test_analytic_entry_dimension(self):
        """Test dimension creation on analytic entry creation
        """
        values = {
            'account_id': self.analytic_account_id,
            'name': 'test',
            'tag_ids': [(6, 0, [self.analytic_tag_type_a.id,
                                self.analytic_tag_concept_a.id,
                                self.analytic_tag_test_a.id])]
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
