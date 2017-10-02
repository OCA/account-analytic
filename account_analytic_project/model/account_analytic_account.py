# -*- coding: utf-8 -*-
# © 2015 Therp BV (http://therp.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class AccountAnalyticAccount(models.Model):
    """Extend account.analytic.account."""
    _inherit = 'account.analytic.account'

    @api.multi
    def create_project_for_account(self):
        """Create a project for an already existing analytic account."""
        project_model = self.env['project.project']
        for this in self:
            if not this.project_ids:
                project_model.create({
                    'name': this.name,
                    'analytic_account_id': this.id,
                })
