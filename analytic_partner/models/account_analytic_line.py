# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    other_partner_id = fields.Many2one(
        comodel_name='res.partner', string="Other Partner",
        domain="['|', ('parent_id', '=', False), ('is_company', '=', True)]")
