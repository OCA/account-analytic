# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line', inverse_name='other_partner_id',
        string='Timesheet activities')
    timesheet_count = fields.Integer(
        string='Timesheet Activities Number',
        compute='_compute_timesheet_count', store=True)

    @api.depends('timesheet_ids')
    def _compute_timesheet_count(self):
        for partner in self:
            partner.timesheet_count = len(partner.timesheet_ids)
