# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticDefault(models.Model):

    _inherit = "account.analytic.default"

    analytic_tag_ids = fields.Many2many('account.analytic.tag',
                                        string="Analytic tags")

    @api.multi
    @api.constrains('analytic_id', 'analytic_tag_ids')
    def _check_required(self):
        # As at least one field of analytic_id and tag_ids is required we throw
        # a validation error should both fields be empty
        for default in self:
            if not default.analytic_id and not default.analytic_tag_ids:
                raise ValidationError(_(
                    'At least one Analytic Account or Analytic Tag has to be '
                    'defined.'))


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        rec = self.env['account.analytic.default'].account_get(
            self.product_id.id, self.invoice_id.partner_id.id, self.env.uid,
            fields.Date.today(), company_id=self.company_id.id)
        self.analytic_tag_ids = rec.analytic_tag_ids.ids
        return res
