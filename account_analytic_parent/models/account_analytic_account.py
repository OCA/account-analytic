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
        for account in self:
            account.debit += sum(account.mapped('child_ids.debit'))
            account.credit += sum(account.mapped('child_ids.credit'))
            account.balance += sum(account.mapped('child_ids.balance'))

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
