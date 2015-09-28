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
from openerp import _, api, models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _compute_has_projects(self):
        """Check wether any project for this analytic account."""
        for this in self:
            this.has_projects = bool(this.project_ids)

    @api.multi
    def create_project_for_account(self):
        """Create a project for an already existing analytic account."""
        project_model = self.env['project.project']
        for this in self:
            if not this.has_projects and this.type != 'view':
                project_model.create({
                    'name': this.name,
                    'analytic_account_id': this.id,
                })

    @api.multi
    def view_projects_for_account(self):
        """View list or form for project(s) related to analytic account."""
        self.ensure_one()
        project_ids = self.project_ids
        assert project_ids, (_(
            'This method is only valid for an analytic account having projects'
        ))
        # Show form by default:
        views = [(False, 'form')]
        action_name = _('Project')
        domain = [('id', 'in', project_ids.ids)]
        res_id = project_ids[-1:].id
        if len(project_ids) > 1:
            # In the future there might be more projects per analytic account,
            # in that case we will show a tree:
            views = [(False, 'tree'), (False, 'form')]
            action_name = _('Projects')
            res_id = False
        return {
            'type': 'ir.actions.act_window',
            'name': action_name,
            'views': views,
            'res_model': 'project.project',
            'res_id': res_id,
            'domain': domain,
        }

    has_projects = fields.Boolean(
        'Has projects', compute='_compute_has_projects')
    project_ids = fields.One2many(
        'project.project', 'analytic_account_id', string='Projects')
