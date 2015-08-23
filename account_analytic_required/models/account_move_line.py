# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account analytic required module for OpenERP
#    Copyright (C) 2011 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#    Developped during the Akretion-Camptocamp code sprint of June 2011
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

from openerp import models, fields, api, _


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    @api.model
    def _get_policies(self):
        """This is the method to be inherited for adding policies"""
        return [('optional', _('Optional')),
                ('always', _('Always')),
                ('never', _('Never'))]

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type in ['none', 'asset', 'liabilty']:
            self.analytic_policy = 'never'
        else:
            self.analytic_policy = 'optional'

    @api.model
    def _default_policy(self):
        return 'optional'

    analytic_policy = fields.Selection(
        '_get_policies', string='Policy for analytic account',
        required=True, default=_default_policy,
        help="Set the policy for analytic accounts : if you select "
        "'Optional', the accountant is free to put an analytic account "
        "on an account move line with this type of account ; if you "
        "select 'Always', the accountant will get an error message if "
        "there is no analytic account ; if you select 'Never', the "
        "accountant will get an error message if an analytic account "
        "is present.")


class AccountAccount(models.Model):
    _inherit = "account.account"

    analytic_policy = fields.Selection(
        string='Policy for analytic account',
        related='user_type.analytic_policy', readonly=True)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_policy = fields.Selection(
        string='Policy for analytic account',
        related='account_id.analytic_policy', readonly=True)
    move_state = fields.Selection(
        string='Move State',
        related='move_id.state',
        default='draft',  # required for view attrs before object is created
        readonly=True)

    def _get_analytic_policy(self, cr, uid, account, context=None):
        """ Extension point to obtain analytic policy for an account """
        return account.user_type.analytic_policy

    def _check_analytic_required_msg(self, cr, uid, ids, context=None):
        for move_line in self.browse(cr, uid, ids, context):
            if move_line.debit == 0 and move_line.credit == 0:
                continue
            analytic_policy = self._get_analytic_policy(cr, uid,
                                                        move_line.account_id,
                                                        context=context)
            if analytic_policy == 'always' and \
                    not move_line.analytic_account_id:
                return _("Analytic policy is set to 'Always' with account "
                         "%s '%s' but the analytic account is missing in "
                         "the account move line with label '%s'.") % \
                        (move_line.account_id.code,
                         move_line.account_id.name,
                         move_line.name)
            elif analytic_policy == 'never' and \
                    move_line.analytic_account_id:
                return _("Analytic policy is set to 'Never' with account %s "
                         "'%s' but the account move line with label '%s' "
                         "has an analytic account %s '%s'.") % \
                        (move_line.account_id.code,
                         move_line.account_id.name,
                         move_line.name,
                         move_line.analytic_account_id.code,
                         move_line.analytic_account_id.name)

    def _check_analytic_required(self, cr, uid, ids, context=None):
        return not self._check_analytic_required_msg(cr, uid, ids,
                                                     context=context)

    _constraints = [(
        _check_analytic_required,
        _check_analytic_required_msg,
        ['analytic_account_id', 'account_id', 'debit', 'credit'])]

    def create(self, cr, uid, vals, context=None, check=True):
        account_obj = self.pool['account.account']
        account = account_obj.browse(
            cr, uid, vals.get('account_id'), context=context)
        if account.analytic_policy == 'never':
            if 'analytic_account_id' in vals:
                del vals['analytic_account_id']
        return super(AccountMoveLine, self).create(
            cr, uid, vals, context=context, check=check)

    def write(self, cr, uid, ids, vals, context=None,
              check=True, update_check=True):
        account_obj = self.pool['account.account']
        for aml in self.browse(cr, uid, ids, context=context):
            if 'account_id' in vals:
                account = account_obj.browse(
                    cr, uid, vals['account_id'], context=context)
                if account.analytic_policy == 'never':
                    vals['analytic_account_id'] = False
        return super(AccountMoveLine, self).write(
            cr, uid, ids, vals, context=context,
            check=check, update_check=update_check)
