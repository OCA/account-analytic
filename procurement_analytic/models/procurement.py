# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
    )
