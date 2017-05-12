# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class AccountAnalyticChart(models.TransientModel):
    _inherit = 'account.analytic.chart'

    @api.multi
    def analytic_account_chart_open_window(self):
        res = super(AccountAnalyticChart,
                    self).analytic_account_chart_open_window()
        ctx = res['context']
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account_analytic_parent', 'action_analytic_account_report')
        res = dict(res.items() + action.items())
        res['context'] = ctx
        return res
