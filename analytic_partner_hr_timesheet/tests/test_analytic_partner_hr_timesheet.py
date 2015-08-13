# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestAnalyticPartnerHrTimesheet(common.TransactionCase):

    def setUp(self):
        super(TestAnalyticPartnerHrTimesheet, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.other_partner = self.env.ref('base.res_partner_3')
        self.analytic_account = self.env['account.analytic.account'].create(
            {'name': 'Test Analytic Account',
             'state': 'draft',
             'partner_id': self.partner.id,
             'type': 'normal'}
        )
        self.hr_analytic_timesheet = self.env['hr.analytic.timesheet'].create(
            {'name': 'Test Timesheet Activity',
             'user_id': self.env.ref('base.user_root').id,
             'journal_id': self.env.ref('hr_timesheet.analytic_journal').id,
             'account_id': self.analytic_account.id,
             'other_partner_id': self.other_partner.id}
        )

    def test_partner_from_hr_timesheet(self):
        self.assertEqual(
            self.hr_analytic_timesheet.line_id.other_partner_id,
            self.other_partner,
            'Timesheet activity partner has not been propagated to the '
            'analytic line on creation')

    def test_change_partner_in_hr_timesheet(self):
        other_partner = self.env.ref('base.res_partner_2')
        self.hr_analytic_timesheet.other_partner_id = other_partner
        self.assertEqual(
            self.hr_analytic_timesheet.line_id.other_partner_id, other_partner,
            'Timesheet activity partner has not been propagated to the '
            'analytic line on write')

    def test_onchange_account_id(self):
        vals = self.env['hr.analytic.timesheet'].on_change_account_id(
            self.analytic_account.id)
        self.assertEqual(self.partner.id, vals['value']['partner_id'])
