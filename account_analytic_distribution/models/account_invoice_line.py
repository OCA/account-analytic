# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    analytic_distribution_id = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic distribution',
    )
