# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# © 2017 Daniel Rodriguez - <drl.9319@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def asset_create(self, lines):
        """Propagate the analytic account from the invoice"""
        res = super(AccountInvoceLine, self).asset_create(lines)
        for line in lines:
            if line.asset_category_id and line.analytics_id:
                asset = self.env['account.asset.asset'].search([
                    ('code', '=', line.invoice_id.number),
                    ('company_id', '=', line.company_id.id),
                ], limit=1)
                if asset:
                    asset.analytic_distribution_id = line.analytics_id.id
        return res
