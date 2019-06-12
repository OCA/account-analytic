# -*- coding: utf-8 -*-
# Copyright 2019 Abraham Anes - <abraham@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def asset_create(self):
        """Propagate the analytic distribution from the invoice line"""
        res = super(AccountInvoiceLine, self).asset_create()
        for line in self:
            if line.asset_category_id and line.analytic_distribution_id:
                asset = self.env['account.asset.asset'].search([
                    ('code', '=', line.invoice_id.number),
                    ('company_id', '=', line.company_id.id),
                ], limit=1)
                if asset:
                    analytic_distribution = line.analytic_distribution_id
                    asset.analytic_distribution_id = analytic_distribution.id
        return res
