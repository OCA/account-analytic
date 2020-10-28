# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.addons.analytic_tag_dimension.tests.test_analytic_dimension import (
    TestAnalyticDimensionBase
)
from odoo.exceptions import ValidationError


class TestAnalyticDimensionCase(TestAnalyticDimensionBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_obj = cls.env['account.account']
        cls.model_obj = cls.env['ir.model']
        cls.field_obj = cls.env['ir.model.fields']
        cls.invoice = cls.env['account.invoice'].create({
            'journal_id': cls.journal.id,
            'partner_id': cls.partner.id,
        })
        # Mock data for testing model dimension, by_sequence with fitered
        vals = {'name': 'A',
                'line_ids': [  # use sequence as record identifier
                    (0, 0, {'value': 'percent', 'sequence': 1001, }),
                    (0, 0, {'value': 'balance', 'sequence': 1002, }),
                ]}
        cls.payterm_a = cls.env['account.payment.term'].create(vals)

    def test_invoice_line_dimension_required(self):
        """If dimension is marked as required,
        I expect error on save if the required dimension is not selected
        """
        self.dimension_1.required = True
        self.dimension_2.required = True

        values = {
            'name': 'test',
            'price_unit': 1,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
            'account_analytic_id': self.analytic_account.id,
            'analytic_tag_ids': [
                (6, 0, [
                    self.analytic_tag_1a.id,
                ]),
            ],
        }
        invoice_line_obj = self.env['account.invoice.line']
        # Error if missing required dimension
        with self.assertRaises(ValidationError):
            invoice_line_obj.create(values)
        self.invoice.invoice_line_ids.unlink()
        values['analytic_tag_ids'] = [(6, 0, [self.analytic_tag_1a.id,
                                              self.analytic_tag_2a.id])]
        # Valid if all required dimension is filled
        line = invoice_line_obj.create(values)
        self.assertTrue(
            line.x_dimension_test_dim_1.id == self.analytic_tag_1a.id)
        self.assertTrue(
            line.x_dimension_test_dim_2.id == self.analytic_tag_2a.id)

    def test_invoice_line_dimension_by_sequence(self):
        """If dimension is by sequence, I expect,
        - No duplicated sequence
        - Selection allowed by sequence, i.e., Concept then Type
        """
        invoice_line_obj = self.env['account.invoice.line']
        # Test no dimension with any sequence
        values = {
            'name': 'test no sequence',
            'price_unit': 1,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
            'account_analytic_id': self.analytic_account.id,
        }
        line = invoice_line_obj.create(values)
        res = line._compute_analytic_tags_domain()
        self.assertFalse(res['domain']['analytic_tag_ids'])
        # Now, user will see tags in sequence 1) Type 2) Concept
        self.dimension_1.write({
            'required': False,
            'by_sequence': True,
            'sequence': 1
        })
        with self.assertRaises(ValidationError):
            self.dimension_2.write({
                'required': False,
                'by_sequence': True,
                'sequence': 1
            })
        self.dimension_2.write({
            'required': False,
            'by_sequence': True,
            'sequence': 2
        })
        # Now, user will see tags in sequence 1) Type 2) Concept
        values = {
            'name': 'test sequence',
            'price_unit': 1,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
            'account_analytic_id': self.analytic_account.id,
        }
        line = invoice_line_obj.create(values)
        # First selection, dimension 1 tag shouldn't be in the domain
        res = line._compute_analytic_tags_domain()
        tag_ids = res['domain']['analytic_tag_ids'][0][2]
        self.assertNotIn(self.analytic_tag_2a.id, tag_ids)
        # Select a dimension 1 tag
        line.analytic_tag_ids += self.analytic_tag_1a
        res = line._compute_analytic_tags_domain()
        tag_ids = res['domain']['analytic_tag_ids'][0][2]
        # Test that all dimension 1 tags are not in list
        type_tag_ids = [self.analytic_tag_1a.id,
                        self.analytic_tag_1b.id]
        for type_tag_id in type_tag_ids:
            self.assertNotIn(type_tag_id, tag_ids)

    def test_zz_invoice_line_dimension_ref_model_with_filter(self):
        """
        For dimension tags created by ref model with by_sequence and filtered,
        We expected that,
        - If user select A, user can only select payment term line 1001, 1002
        Note:
            We use payment term and payment term line for testing purposes,
            although it does not make sense in real life
        # """
        # It should be executed the last one for avoiding side effects
        # as not everything is undone in this removal
        # Clear all dimension
        self.tag_obj.search([]).unlink()
        self.dimension_obj.search([]).unlink()
        # Create new dimension, using reference model
        pt = self.model_obj.search([('model', '=', 'account.payment.term')])
        pt_dimension = self.dimension_obj.create({'name': 'Payment Term',
                                                  'code': 'payterm',
                                                  'by_sequence': True,
                                                  'sequence': 1, })
        pt_dimension.create_analytic_tags()  # Test create without model
        pt_dimension.ref_model_id = pt
        pt_dimension.create_analytic_tags()
        ptl = self.model_obj.search([('model', '=',
                                      'account.payment.term.line')])
        # Payment term line will be filtered with payment_id
        ptl_dimension = self.dimension_obj.create({'name': 'Payment Term Line',
                                                   'code': 'payterm_line',
                                                   'ref_model_id': ptl.id,
                                                   'by_sequence': True,
                                                   'sequence': 2,
                                                   })
        filter_field = self.field_obj.search([('model_id', '=', ptl.id),
                                              ('name', '=', 'payment_id')])
        ptl_dimension.filtered_field_ids += filter_field
        ptl_dimension.create_analytic_tags()
        values = {
            'name': 'test',
            'price_unit': 1,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
            'account_analytic_id': self.analytic_account.id,
        }
        invoice_line_obj = self.env['account.invoice.line']
        line = invoice_line_obj.create(values)
        tag = self.tag_obj.search([('name', '=', 'A')])
        line.analytic_tag_ids += tag
        res = line._compute_analytic_tags_domain()
        # Test whether this will list only 2 tags of payment term line 1001, 1002
        tag_ids = res['domain']['analytic_tag_ids'][0][2]
        tags = self.tag_obj.search([('id', 'in', tag_ids)])
        sequences = tags.mapped('resource_ref').mapped('sequence')
        self.assertEquals(set([1001, 1002]), set(sequences))
