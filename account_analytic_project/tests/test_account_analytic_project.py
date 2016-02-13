# -*- coding: utf-8 -*-
# © 2015 Therp BV (http://therp.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestAccountAnalyticProject(TransactionCase):

    def test_account_analytic_project(self):
        account = self.env['account.analytic.account'].search([
            ('project_ids', '=', False),
        ], limit=1)
        account.create_project_for_account()
        action = account.view_projects_for_account()
        self.assertEqual(
            self.env['project.project'].browse([action['res_id']]),
            account.project_ids)
