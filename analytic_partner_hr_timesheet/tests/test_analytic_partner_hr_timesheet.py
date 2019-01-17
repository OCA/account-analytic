# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestAnalyticPartnerHrTimesheet(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAnalyticPartnerHrTimesheet, cls).setUpClass()
        cls.partner_line = cls.env['res.partner'].create({
            'name': 'Test Partner Line',
        })
        cls.partner_project = cls.env['res.partner'].create({
            'name': 'Test Partner Project',
        })
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
        })
        cls.project = cls.env['project.project'].create({
            'name': 'Test Project',
            'partner_id': cls.partner_project.id
        })
        cls.line = cls.env['account.analytic.line'].create({
            'account_id': cls.analytic_account.id,
            'name': 'Test Line',
            'partner_id': cls.partner_line.id,
        })

    def test_onchange_project_id(self):
        self.line.project_id = self.project.id
        self.line.onchange_project_id()
        self.assertEqual(self.line.partner_id,
                         self.line.project_id.partner_id)

    def test_compute_timesheet_count(self):
        self.line.other_partner_id = self.partner_line.id
        self.partner_line._compute_timesheet_count()
        self.assertEqual(
            self.partner_line.timesheet_count, 1)
