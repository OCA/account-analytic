# -*- coding: utf-8 -*-
# Copyright 2017 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestAnalyticDistribution(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAnalyticDistribution, cls).setUpClass()
        cls.account1 = cls.env['account.analytic.account'].create({
            'name': 'Test account #1',
        })
        cls.account2 = cls.env['account.analytic.account'].create({
            'name': 'Test account #2',
        })
        cls.invoice_model = cls.env['account.invoice']
        cls.distribution = cls.env['account.analytic.distribution'].create({
            'name': 'Test distribution initial',
            'rule_ids': [
                (0, 0, {
                    'sequence': 10,
                    'percent': 75.00,
                    'analytic_account_id': cls.account1.id,
                }),
                (0, 0, {
                    'sequence': 20,
                    'percent': 25.00,
                    'analytic_account_id': cls.account2.id,
                }),
            ]
        })
        cls.user_type = cls.env.ref('account.data_account_type_revenue')
        cls.invoice = cls.invoice_model.create({
            'partner_id': cls.env.ref('base.res_partner_12').id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Product Test',
                'quantity': 1.0,
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'price_unit': 100.0,
                'account_id': cls.env['account.account'].search([
                    ('user_type_id', '=', cls.user_type.id)], limit=1).id,
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
