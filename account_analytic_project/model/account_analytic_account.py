# -*- encoding: utf-8 -*-
"""Extend account.analytic.account."""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV <http://therp.nl>
#    All Rights Reserved
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
from openerp.osv import orm, fields


class AccountAnalyticAccount(orm.Model):
    """Extend account.analytic.account."""
    _inherit = 'account.analytic.account'

    def _has_projects(self, cr, uid, ids, name, arg, context=None):
        """Check wether any project for this analytic account."""
        project_model = self.pool['project.project']
        res = {}
        for analytic_id in ids:
            has_project = False
            project_ids = project_model.search(
                cr, uid, [('analytic_account_id', '=', analytic_id)],
                context=context
            )
            if project_ids:
                has_project = True
            res[analytic_id] = has_project
        return res

    def create_project_for_account(self, cr, uid, ids, context=None):
        """Create a project for an already existing analytic account."""
        project_model = self.pool['project.project']
        for this_obj in self.browse(cr, uid, ids, context=context):
            if not this_obj.has_projects and this_obj.type != 'view':
                project_id = project_model.create(
                    cr, uid, {
                        'name': this_obj.name,
                        'analytic_account_id': this_obj.id,
                    },
                    context=context
                )
        return True

    _columns = {
        'has_projects': fields.function(
            _has_projects, type='boolean', string='Has projects',),
    }
