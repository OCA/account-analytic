# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    timesheets = fields.One2many(
        comodel_name='hr.analytic.timesheet', inverse_name='other_partner_id',
        string='Timesheet activities')
    timesheet_count = fields.Integer(
        string='Timesheet Activities Number',
        compute='compute_timesheet_count', store=True)

    @api.one
    @api.depends('timesheets')
    def compute_timesheet_count(self):
        self.timesheet_count = len(self.timesheets)
