# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    analytic_policy = fields.Selection(
        string='Policy for analytic account',
        related='account_id.analytic_policy', readonly=True)
    invoice_state = fields.Selection(
        string='Invoice State',
        default='draft',
        related='invoice_id.state', readonly=True)

    @api.multi
    def onchange_account_id(self, product_id, partner_id, inv_type,
                            fposition_id, account_id):
        res = super(AccountInvoiceLine, self).onchange_account_id(
            product_id, partner_id, inv_type, fposition_id, account_id)
        account = self.env['account.account'].browse(account_id)
        if account.analytic_policy == 'never':
            if not res.get('value'):
                res.update({'value': {'account_analytic_id': False}})
            else:
                res['value'].update({'account_analytic_id': False})
        return res

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        account = self.env['account.account'].browse(vals.get('account_id'))
        if account.analytic_policy == 'never':
            if 'analytic_account_id' in vals:
                del vals['account_analytic_id']
        return super(AccountInvoiceLine, self).create(vals)

    @api.multi
    def write(self, vals):
        for aml in self:
            if 'account_id' in vals:
                account = self.env['account.account'].browse(
                    vals['account_id'])
                if account.analytic_policy == 'never':
                    vals['account_analytic_id'] = False
        return super(AccountInvoiceLine, self).write(vals)
