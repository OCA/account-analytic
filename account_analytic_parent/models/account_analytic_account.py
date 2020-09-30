# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    parent_left = fields.Integer(
        string='Left Parent',
        index=True,
    )
    parent_right = fields.Integer(
        string='Right Parent',
        index=True,
    )
    parent_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Parent Analytic Account",
        index=True,
        ondelete='cascade',
    )
    child_ids = fields.One2many(
        comodel_name="account.analytic.account",
        inverse_name="parent_id",
        string="Child Accounts", copy=True,
    )
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True,
    )

    @api.multi
    def _compute_debit_credit_balance(self):
        """
        Warning, this method overwrites the standard because the hierarchy
        of analytic account changes
        """
        super()._compute_debit_credit_balance()
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
            account.debit = abs(data_debit)
            account.credit = data_credit
            account.balance = account.credit - account.debit

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for account in self:
            if account.parent_id:
                account.complete_name = _('%(parent)s / %(own)s') % {
                    'parent': account.parent_id.complete_name,
                    'own': account.name,
                }
            else:
                account.complete_name = account.name

    @api.depends(
        'complete_name',
        'code',
        'partner_id.commercial_partner_id.name',
    )
    def _compute_display_name(self):
        super()._compute_display_name()

    @api.multi
    @api.constrains("parent_id")
    def check_recursion(self):
        for account in self:
            if not super(AccountAnalyticAccount, account)._check_recursion():
                raise UserError(
                    _("You can not create recursive analytic accounts."),
                )

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
    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        for account in self:
            account.partner_id = account.parent_id.partner_id

    @api.multi
    def name_get(self):
        res = []
        for analytic in self:
            name = analytic.complete_name
            if analytic.code:
                name = _('[%(code)s] %(name)s') % {
                    'code': analytic.code,
                    'name': name,
                }
            if analytic.partner_id:
                name = _('%(name)s - %(partner)s') % {
                    'name': name,
                    'partner': analytic.partner_id.commercial_partner_id.name,
                }
            res.append((analytic.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super().name_search(
            name, args, operator,limit)
        if operator not in ('ilike', 'like', '=', '=like', '=ilike'):
            return res
        account_ids = {pair[0] for pair in res} if res else set()
        recs = self.search([('complete_name', operator, name)])
        account_ids.update(recs.ids)
        return self.browse(account_ids).name_get()

    @api.multi
    def write(self, vals):
        if self and 'active' in vals and not vals['active']:
            self.mapped('child_ids').write({'active': False})
        return super().write(vals)
