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

    analytic_policy = fields.Selection(
        '_get_policies', string='Policy for analytic account',
        required=True, default=lambda self: self._default_policy(),
        help="Set the policy for analytic accounts : if you select "
        "'Optional', the accountant is free to put an analytic account "
        "on an account move line with this type of account ; if you "
        "select 'Always', the accountant will get an error message if "
        "there is no analytic account ; if you select 'Never', the "
        "accountant will get an error message if an analytic account "
        "is present.")

    @api.model
    def _get_policies(self):
        """This is the method to be inherited for adding policies"""
        return [('optional', _('Optional')),
                ('always', _('Always')),
                ('never', _('Never'))]

    @api.model
    def _default_policy(self):
        return 'optional'

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type in ['none', 'asset', 'liabilty']:
            self.analytic_policy = 'never'
        else:
            self.analytic_policy = 'optional'
