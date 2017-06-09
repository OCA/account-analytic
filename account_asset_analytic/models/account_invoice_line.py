# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def asset_create(self):
        """Propagate the analytic account from the invoice"""
        res = super(AccountInvoiceLine, self).asset_create()
        for line in self:
            if line.asset_category_id and line.account_analytic_id:
                asset = self.env['account.asset.asset'].search([
                    ('code', '=', line.invoice_id.number),
                    ('company_id', '=', line.company_id.id),
                ], limit=1)
                if asset:
                    asset.analytic_account_id = line.account_analytic_id.id
        return res
