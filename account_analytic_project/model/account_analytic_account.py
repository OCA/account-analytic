# -*- coding: utf-8 -*-
# © 2015 Therp BV (http://therp.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models


class AccountAnalyticAccount(models.Model):
    """Extend account.analytic.account."""
    _inherit = 'account.analytic.account'

    @api.multi
    def create_project_for_account(self):
        """Create a project for an already existing analytic account."""
        project_model = self.env['project.project']
        for this in self:
            if not this.project_ids and this.type != 'view':
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
            'This method is only valid for an analytic account'
            ' having projects.'
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

    project_ids = fields.One2many(
        'project.project', 'analytic_account_id', string='Projects')
