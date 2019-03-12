# -*- coding: utf-8 -*-
# Copyright 2017 - Tecnativa - Vicent Cubells
# Copyright 201p - Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAnalyticDistribution(TransactionCase):

    def setUp(self):
        super(TestAnalyticDistribution, self).setUp()
        self.account1 = self.env['account.analytic.account'].create({
            'name': 'Test account #1',
        })
        self.account2 = self.env['account.analytic.account'].create({
            'name': 'Test account #2',
        })
        self.tag1 = self.env['account.analytic.tag'].create({
            'name': 'Test analytic tag #1',
        })
        self.tag2 = self.env['account.analytic.tag'].create({
            'name': 'Test analytic tag #2',
        })
        self.invoice_model = self.env['account.invoice']
        self.distribution = self.env['account.analytic.distribution'].create({
            'name': 'Test distribution initial',
            'rule_ids': [
                (0, 0, {
                    'sequence': 10,
                    'percent': 75.00,
                    'analytic_account_id': self.account1.id,
                    'analytic_tag_ids': [(6, 0, [self.tag1.id, self.tag2.id])]
                }),
                (0, 0, {
                    'sequence': 20,
                    'percent': 25.00,
                    'analytic_account_id': self.account2.id,
                    'analytic_tag_ids': [(6, 0, self.tag2.ids)]
                }),
            ]
        })
        self.user_type = self.env.ref('account.data_account_type_revenue')
        self.invoice = self.invoice_model.create({
            'partner_id': self.env.ref('base.res_partner_12').id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Product Test',
                'quantity': 1.0,
                'uom_id': self.env.ref('product.product_uom_unit').id,
                'price_unit': 100.0,
                'account_id': self.env['account.account'].search([
                    ('user_type_id', '=', self.user_type.id)], limit=1).id,
            })]
        })

    def test_partner_invoice(self):
        # Save values to compare later
        count1 = len(self.account1.line_ids.ids)
        count2 = len(self.account2.line_ids.ids)
        amount1 = sum(self.account1.line_ids.mapped('amount'))
        amount2 = sum(self.account2.line_ids.mapped('amount'))
        self.invoice.invoice_line_ids[0].analytic_distribution_id = \
            self.distribution.id
        self.invoice.journal_id.group_invoice_lines = True
        self.invoice.action_invoice_open()
        # One line by account has been created only
        self.assertEqual(len(self.account1.line_ids.ids), count1 + 1)
        self.assertEqual(len(self.account2.line_ids.ids), count2 + 1)
        # Check amount
        self.assertAlmostEqual(
            self.account1.balance, amount1 + 75.0)
        self.assertAlmostEqual(
            self.account2.balance, amount2 + 25.0)
        # Check tags
        self.assertEqual(len(self.account1.line_ids.mapped('tag_ids')), 2)
        self.assertEqual(len(self.account2.line_ids.mapped('tag_ids')), 1)

    def test_sum_percent_rules(self):
        # Check incorrect sum of rules
        self.env.user.company_id.force_percent = False
        # We can create an analytic distribution
        self.env['account.analytic.distribution'].create({
            'name': 'Test distribution',
            'rule_ids': [
                (0, 0, {
                    'sequence': 10,
                    'percent': 75.00,
                    'analytic_account_id': self.account1.id,
                }),
            ]
        })
        # Force percent for company
        self.env.user.company_id.force_percent = True
        # Unable to create an analytic distribution
        with self.assertRaises(ValidationError):
            self.env['account.analytic.distribution'].create({
                'name': 'Test distribution constraint',
                'rule_ids': [
                    (0, 0, {
                        'sequence': 10,
                        'percent': 75.00,
                        'analytic_account_id': self.account1.id,
                    }),
                ]
            })

    def test_check_uniq_rule(self):
        with self.assertRaises(ValidationError):
            self.distribution.rule_ids[0].copy()
