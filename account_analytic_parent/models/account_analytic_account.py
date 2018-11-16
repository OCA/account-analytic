# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    parent_id = fields.Many2one(
        'account.analytic.account',
        string='Parent Analytic Account'
    )
    child_ids = fields.One2many('account.analytic.account', 'parent_id',
                                'Child Accounts', copy=True)

    @api.multi
    def _compute_debit_credit_balance(self):
        """
        Warning, this method overwrites the standard because the hierarchy
        of analytic account changes
        """
        super(AccountAnalyticAccount, self)._compute_debit_credit_balance()
        analytic_line_obj = self.env['account.analytic.line']
        # compute only analytic line
        for account in self.filtered(lambda x: x.child_ids):
            domain = [('account_id', 'child_of', account.ids)]
            credit_groups = analytic_line_obj.read_group(
                domain=domain + [('amount', '>', 0.0)],
                fields=['account_id', 'amount'],
                groupby=['account_id']
            )
            data_credit = sum(l['amount'] for l in credit_groups)
            debit_groups = analytic_line_obj.read_group(
                domain=domain + [('amount', '<', 0.0)],
                fields=['account_id', 'amount'],
                groupby=['account_id']
            )
            data_debit = sum(l['amount'] for l in debit_groups)
            account.debit = data_debit
            account.credit = data_credit
            account.balance = account.credit - account.debit

    @api.multi
    @api.constrains('parent_id')
    def check_recursion(self):
        for account in self:
            if not super(AccountAnalyticAccount, account)._check_recursion():
                raise UserError(
                    _('You can not create recursive analytic accounts.'),
                )

    @api.multi
    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        for account in self:
            account.partner_id = account.parent_id.partner_id

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for account in self:
            current = account
            name = current.name
            while current.parent_id:
                name = '%s / %s' % (current.parent_id.name, name)
                current = current.parent_id
            res.append((account.id, name))
        return res

    @api.multi
    @api.constrains('active')
    def check_parent_active(self):
        for account in self:
            if (account.active and account.parent_id and
                    account.parent_id not in self and
                    not account.parent_id.active):
                raise UserError(
                    _('Please activate first parent account %s')
                    % account.parent_id.display_name)

    @api.multi
    def write(self, vals):
        if self and 'active' in vals and not vals['active']:
            self.mapped('child_ids').write({'active': False})
        return super(AccountAnalyticAccount, self).write(vals)
