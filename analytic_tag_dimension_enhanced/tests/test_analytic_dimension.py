# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestAnalyticDimensionCase(SavepointCase):

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super(TestAnalyticDimensionCase, cls).setUpClass(*args, **kwargs)

        cls.dimension_obj = cls.env['account.analytic.dimension']
        cls.tag_obj = cls.env['account.analytic.tag']
        cls.analytic_line_obj = cls.env['account.analytic.line']
        cls.account_obj = cls.env['account.account']
        cls.model_obj = cls.env['ir.model']
        cls.field_obj = cls.env['ir.model.fields']

        cls.analytic_dimension_type = cls.env.ref(
            'analytic_tag_dimension.analytic_dimension_type')
        cls.analytic_dimension_concept = cls.env.ref(
            'analytic_tag_dimension.analytic_dimension_concept')
        cls.analytic_tag_type_a = cls.env.ref(
            'analytic_tag_dimension.analytic_tag_type_a')
        cls.analytic_tag_type_b = cls.env.ref(
            'analytic_tag_dimension.analytic_tag_type_b')
        cls.analytic_tag_concept_a = cls.env.ref(
            'analytic_tag_dimension.analytic_tag_concept_a')
        cls.analytic_tag_concept_b = cls.env.ref(
            'analytic_tag_dimension.analytic_tag_concept_b')

        cls.account_analytic_id = cls.env.ref(
            'analytic.analytic_absences').id

        cls.account_user_type = cls.env.ref(
            'account.data_account_type_receivable')

        cls.journal = cls.env['account.journal'].create(
            {'name': 'Test  Journal',
             'code': 'TJ',
             'type': 'general'
             }
        )

        cls.company_id = cls.env['res.users'].browse(
            cls.env.uid).company_id.id

        cls.partner = cls.env.ref('base.res_partner_2')
        cls.account = cls.account_obj.create({
            'code': 'test_dimension_acc_02',
            'name': 'test dimension account',
            'user_type_id': cls.account_user_type.id,
            'reconcile': True,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'journal_id': cls.journal.id,
            'company_id': cls.company_id,
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
        self.analytic_dimension_type.required = True
        self.analytic_dimension_concept.required = True

        values = {
            'name': 'test',
            'price_unit': 1,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
            'account_analytic_id': self.account_analytic_id,
            'analytic_tag_ids': [
                (6, 0, [
                    self.analytic_tag_type_a.id,
                ]),
            ],
        }
        invoice_line_obj = self.env['account.invoice.line']
        # Error if missing required dimension
        with self.assertRaises(ValidationError):
            invoice_line_obj.create(values)
        self.invoice.invoice_line_ids.unlink()
        values['analytic_tag_ids'] = [(6, 0, [self.analytic_tag_type_a.id,
                                              self.analytic_tag_concept_a.id])]
        # Valid if all required dimension is filled
        line = invoice_line_obj.create(values)
        self.assertTrue(
            line.x_dimension_type.id == self.analytic_tag_type_a.id)
        self.assertTrue(
            line.x_dimension_concept.id == self.analytic_tag_concept_a.id)

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
            'account_analytic_id': self.account_analytic_id,
        }
        line = invoice_line_obj.create(values)
        res = line._compute_analytic_tags_domain()
        self.assertFalse(res['domain']['analytic_tag_ids'])

        # Now, user will see tags in sequence 1) Type 2) Concept
        self.analytic_dimension_type.write({'required': False,
                                            'by_sequence': True,
                                            'sequence': 1, })
        with self.assertRaises(ValidationError):
            self.analytic_dimension_concept.write({'required': False,
                                                   'by_sequence': True,
                                                   'sequence': 1, })
        self.analytic_dimension_concept.write({'required': False,
                                               'by_sequence': True,
                                               'sequence': 2, })
        # Now, user will see tags in sequence 1) Type 2) Concept
        values = {
            'name': 'test sequence',
            'price_unit': 1,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
            'account_analytic_id': self.account_analytic_id,
        }
        line = invoice_line_obj.create(values)
        # First selection, Cocept tags shouldn't be in the domain
        res = line._compute_analytic_tags_domain()
        tag_ids = res['domain']['analytic_tag_ids'][0][2]
        # Test that all concept tags is not in list
        concept_tag_ids = [self.analytic_tag_concept_a.id,
                           self.analytic_tag_concept_b.id]
        for concept_tag_id in concept_tag_ids:
            self.assertNotIn(concept_tag_id, tag_ids)
        # Select a type tag
        line.analytic_tag_ids += self.analytic_tag_type_a
        res = line._compute_analytic_tags_domain()
        tag_ids = res['domain']['analytic_tag_ids'][0][2]
        # Test that all concept tags is not in list
        type_tag_ids = [self.analytic_tag_type_a.id,
                        self.analytic_tag_type_b.id]
        for type_tag_id in type_tag_ids:
            self.assertNotIn(type_tag_id, tag_ids)

    def test_invoice_line_dimension_ref_model_with_filter(self):
        """
        For dimension tags created by ref model with by_sequence and filtered,
        We expected that,
        - If user select A, user can only select payment term line 1001, 1002
        Note:
            We use payment term and payment term line for testing purposes,
            although it does not make sense in real life
        # """
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
            'account_analytic_id': self.account_analytic_id,
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
