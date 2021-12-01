# -*- coding:utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def recompute_account_analytic(self):
        '''
        Open the wizard to change the analytical account
        '''
        return {'type': 'ir.actions.act_window',
                'res_model': 'wizard.change.account.analytic',
                'views': [[False, 'form']],
                'context': {'current_analytic_account': self.analytic_account_id.id,
                            'invoice_id': self.id},
                'target': 'new'
                }
