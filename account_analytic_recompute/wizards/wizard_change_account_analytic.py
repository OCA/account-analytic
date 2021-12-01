# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class WizardChangeAccountAnalytic(models.TransientModel):
    _name = 'wizard.change.account.analytic'
    _description = 'Allows you to change the "Analytical account" field of the invoice line in the published status.'

    def change_account_analytic(self):
        '''
        Change the analytical account on the invoice line and create the analytical account lines
        '''
        if self.last_analytic_account_id and self.analytic_account_id == self.last_analytic_account_id:
            raise UserError(u'The new analytical account must be different from the analytical account on the invoice '
                            u'line.')
        move_line_id = self.env['account.move.line'].browse(self._context.get('move_line_id'))
        move_line_id.analytic_account_id = self.analytic_account_id
        move_line_id.create_analytic_lines()

    def default_analytic_account_id(self):
        '''
        Returns the analytic_account_id of invoice line to be placed by default to opening the wizard
        '''
        analytic_account_id = self.env['account.analytic.account'].browse(self._context.get('current_analytic_account'))
        last_analytic_account_id = self.env['account.analytic.account'].browse(self._context.get('current_analytic_account'))
        return analytic_account_id

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        default=default_analytic_account_id,
        check_company=True,
        help=u'Allows you to change the analytical account and fill the table of analytical accounts'
    )
    last_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        default=default_analytic_account_id,
        check_company=True,
        help=u'Allows you to change the analytical account and fill the table of analytical accounts'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env.company,
        help=u'Necessary we only have to show the analytical accounts per company'
    )
