# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Therp BV <http://therp.nl>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests.common import TransactionCase


class TestAccountAnalyticProject(TransactionCase):
    def test_account_analytic_project(self):
        account = self.env['account.analytic.account'].search([
            ('project_ids', '=', False),
        ], limit=1)
        self.assertEqual(account.has_projects, False)
        account.create_project_for_account()
        action = account.view_projects_for_account()
        self.assertEqual(
            self.env['project.project'].browse([action['res_id']]),
            account.project_ids)
        self.assertEqual(account.has_projects, True)
