# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountAnalyticChart(models.TransientModel):
    _name = 'account.analytic.chart'
    _description = 'Account Analytic Chart'

    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')

    @api.multi
    def analytic_account_chart_open_window(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('analytic',
                                              'action_analytic_account_form')
        id = result and result[1] or False
        result = dict(act_obj.with_context(context).browse(id)._context or {})
        if self.from_date:
            result.update({'from_date': self.from_date})
        if self.to_date:
            result.update({'to_date': self.to_date})
        result['context'] = str(result)
        ctx = result['context']
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account_analytic_parent', 'action_analytic_account_report')
        result = dict(result.items() + action.items())
        result['context'] = ctx
        return result
