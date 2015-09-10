# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, fields


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    other_partner_id = fields.Many2one(
        comodel_name='res.partner', string="Other Partner",
        domain="['|', ('parent_id', '=', False), ('is_company', '=', True)]")

    @api.model
    def create(self, vals):
        res = super(HrAnalyticTimesheet, self).create(vals)
        if vals.get('other_partner_id') is not None:
            res.line_id.other_partner_id = vals['other_partner_id']
        return res

    @api.multi
    def write(self, vals):
        res = super(HrAnalyticTimesheet, self).write(vals)
        if vals.get('other_partner_id') is not None:
            self.mapped('line_id').write(
                {'other_partner_id': vals['other_partner_id']})
        return res

    def on_change_account_id(self, cr, uid, ids, account_id, context=False):
        """Signature cannot be new API because of the arguments are badly
        named between hr_timesheet and hr_timesheet_invoice.
        """
        res = super(HrAnalyticTimesheet, self).on_change_account_id(
            cr, uid, ids, account_id, context)
        analytic_account = self.pool['account.analytic.account'].browse(
            cr, uid, account_id)
        res['value'] = res.get('value', {})
        res['value']['partner_id'] = (
            analytic_account.partner_id and analytic_account.partner_id.id or
            False)
        return res
