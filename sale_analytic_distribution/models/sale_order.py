# -*- coding: utf-8 -*-
#  Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#  Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_distribution_id = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic Distribution', oldname='analytics_id',
    )

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'analytic_distribution_id': self.analytic_distribution_id.id,
        })
        return res
