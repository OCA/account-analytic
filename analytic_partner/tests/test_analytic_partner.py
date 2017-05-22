# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


@common.at_install(False)
@common.post_install(True)
class TestAnalyticPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAnalyticPartner, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test account type',
            'type': 'other',
        })
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': cls.account_type.id
        })
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': cls.partner.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Test line',
                    'account_id': cls.account.id,
                    'account_analytic_id': cls.analytic_account.id,
                    'quantity': 10.0,
                    'price_unit': 50.0,
                })
            ]
        })

    def test_flow(self):
        self.invoice.action_invoice_open()
        if self.invoice.move_id.state == 'draft':
            self.invoice.move_id.post()
        analytic_lines = self.invoice.move_id.mapped(
            'line_ids.analytic_line_ids')
        for analytic_line in analytic_lines:
            self.assertEqual(
                analytic_line.other_partner_id,
                self.invoice.partner_id.commercial_partner_id,
                '''Invoice partner has not been propagated
                   to the analytic line''')
