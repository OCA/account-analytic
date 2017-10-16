# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAnalyticTagDefault(TransactionCase):

    def setUp(self):

        super(TestAnalyticTagDefault, self).setUp()

        self.account = self.env['account.account'].create({
            'name': 'Dummy account',
            'code': 'DUMMY',
            'user_type_id': self.env.ref(
                'account.data_account_type_other_income').id
        })

        tag_model = self.env['account.analytic.tag']

        self.tag_a = tag_model.create({
            'name': 'Tag A'
        })
        self.tag_1 = tag_model.create({
            'name': 'Tag 1'
        })
        self.tag_2 = tag_model.create({
            'name': 'Tag 2'
        })

        self.analytic_account_absences = self.env.ref(
            'analytic.analytic_absences')
        self.analytic_account_internal = self.env.ref(
            'analytic.analytic_internal')

        default_model = self.env['account.analytic.default']

        self.service_delivery = self.env.ref('product.service_delivery')
        self.service_order = self.env.ref('product.service_order_01')
        self.service_cost = self.env.ref('product.service_cost_01')

        self.only_account_default = default_model.create({
            'analytic_id': self.analytic_account_absences.id,
            'product_id': self.service_delivery.id
        })

        self.only_tag_default = default_model.create({
            'analytic_tag_ids': [(6, 0, [self.tag_a.id])],
            'product_id': self.service_order.id
        })

        self.multiple_default = default_model.create({
            'analytic_id': self.analytic_account_internal.id,
            'analytic_tag_ids': [(6, 0, [self.tag_1.id, self.tag_2.id])],
            'product_id': self.service_cost.id
        })

    def test_default_get_product(self):

        res = self.env['account.analytic.default'].account_get(
            product_id=self.service_delivery.id)
        self.assertEqual(res, self.only_account_default)

        res = self.env['account.analytic.default'].account_get(
            product_id=self.service_order.id)
        self.assertEqual(res, self.only_tag_default)

        res = self.env['account.analytic.default'].account_get(
            product_id=self.service_cost.id)
        self.assertEqual(res, self.multiple_default)

    def test_default_get_partner(self):
        default_model = self.env['account.analytic.default']
        demo_partner = self.env.ref('base.partner_demo')

        self.partner_default = default_model.create({
            'partner_id': demo_partner.id,
            'analytic_tag_ids': [(6, 0, [self.tag_a.id])],
        })
        res = default_model.account_get(partner_id=demo_partner.id)
        self.assertEqual(self.partner_default, res)

    def test_default_get_user(self):
        default_model = self.env['account.analytic.default']

        self.user_default = default_model.create({
            'user_id': self.env.user.id,
            'analytic_tag_ids': [(6, 0, [self.tag_a.id])],
        })
        res = default_model.account_get(user_id=self.env.user.id)
        self.assertEqual(self.user_default, res)

    def test_default_account(self):

        invoice_object = self.env['account.invoice']
        partner_demo = self.env.ref('base.partner_demo')

        invoice_account = invoice_object.create({
            'partner_id': partner_demo.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.service_delivery.id,
                'price_unit': 1,
                'account_id': self.account.id,
                'name': 'test'
            })]
        })
        invoice_account.invoice_line_ids._onchange_product_id()
        self.assertEqual(invoice_account.invoice_line_ids.account_analytic_id,
                         self.analytic_account_absences)

    def test_default_tags(self):

        invoice_object = self.env['account.invoice']
        partner_demo = self.env.ref('base.partner_demo')

        invoice_one_tag = invoice_object.create({
            'partner_id': partner_demo.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.service_order.id,
                'price_unit': 1,
                'account_id': self.account.id,
                'name': 'test'
            })]
        })
        invoice_one_tag.invoice_line_ids._onchange_product_id()
        self.assertEqual(invoice_one_tag.invoice_line_ids.analytic_tag_ids,
                         self.tag_a)

    def test_default_tag_and_account(self):

        invoice_object = self.env['account.invoice']
        partner_demo = self.env.ref('base.partner_demo')

        invoice_multiple = invoice_object.create({
            'partner_id': partner_demo.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.service_cost.id,
                'price_unit': 1,
                'account_id': self.account.id,
                'name': 'test'
            })]
        })
        invoice_multiple.invoice_line_ids._onchange_product_id()
        self.assertEqual(invoice_multiple.invoice_line_ids.account_analytic_id,
                         self.analytic_account_internal)
        self.assertEqual(len(
            invoice_multiple.invoice_line_ids.analytic_tag_ids), 2)
        self.assertEqual(invoice_multiple.invoice_line_ids.analytic_tag_ids,
                         self.tag_1 + self.tag_2)

    def test_errors(self):

        with self.assertRaises(ValidationError):
            self.only_account_default.write({
                'analytic_id': None
            })

        with self.assertRaises(ValidationError):
            self.env['account.analytic.default'].create({
                'product_id': self.service_delivery.id
            })
