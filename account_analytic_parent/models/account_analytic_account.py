# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


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
            debit = account.debit
            credit = account.credit
            balance = account.balance
            for child in account.child_ids:
                debit += child.debit
                credit += child.credit
                balance += child.balance
            account.debit = debit
            account.credit = credit
            account.balance = balance

    @api.constrains('parent_id')
    @api.one
    def check_recursion(self):
        if not super(AccountAnalyticAccount, self)._check_recursion():
            raise ValidationError(
                _('You can not create recursive analytic accounts.'),
            )

    @api.multi
    @api.onchange('parent_id')
    def on_change_parent(self):
        for account in self:
            account.partner_id = account.parent_id.partner_id or False

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for account_item in self:
            data = []
            proj = account_item

            while proj:
                if proj and proj.name:
                    data.insert(0, proj.name)
                else:
                    data.insert(0, '')

                proj = proj.parent_id
            data = ' / '.join(data)
            res.append((account_item.id, data))
        return res
