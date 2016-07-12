# -*- coding: utf-8 -*-
# © 2011 Akretion
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import _, api, exceptions, fields, models
from openerp.tools import float_is_zero


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    @api.model
    def _get_policies(self):
        """This is the method to be inherited for adding policies"""
        return [('optional', 'Optional'),
                ('always', 'Always'),
                ('never', 'Never')]

    analytic_policy = fields.Selection(
        _get_policies,
        'Policy for analytic account',
        required=True,
        default='optional',
        help="Set the policy for analytic accounts : if you select "
             "'Optional', the accountant is free to put an analytic account "
             "on an account move line with this type of account ; if you "
             "select 'Always', the accountant will get an error message if "
             "there is no analytic account ; if you select 'Never', the "
             "accountant will get an error message if an analytic account "
             "is present.")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_analytic_policy(self, account):
        """ Extension point to obtain analytic policy for an account """
        return account.user_type_id.analytic_policy

    @api.multi
    def _check_analytic_required_msg(self):
        for move_line in self:
            prec = move_line.company_currency_id.rounding
            if (float_is_zero(move_line.debit, precision_rounding=prec) and
                    float_is_zero(move_line.credit, precision_rounding=prec)):
                continue
            analytic_policy = self._get_analytic_policy(move_line.account_id)
            if (analytic_policy == 'always' and
                    not move_line.analytic_account_id):
                return _("Analytic policy is set to 'Always' with account "
                         "%s '%s' but the analytic account is missing in "
                         "the account move line with label '%s'."
                         ) % (move_line.account_id.code,
                              move_line.account_id.name,
                              move_line.name)
            elif (analytic_policy == 'never' and
                    move_line.analytic_account_id):
                return _("Analytic policy is set to 'Never' with account %s "
                         "'%s' but the account move line with label '%s' "
                         "has an analytic account %s '%s'."
                         ) % (move_line.account_id.code,
                              move_line.account_id.name,
                              move_line.name,
                              move_line.analytic_account_id.code,
                              move_line.analytic_account_id.name)

    @api.constrains('analytic_account_id', 'account_id', 'debit', 'credit')
    def _check_analytic_required(self):
        for rec in self:
            message = rec._check_analytic_required_msg()
            if message:
                raise exceptions.ValidationError(message)
