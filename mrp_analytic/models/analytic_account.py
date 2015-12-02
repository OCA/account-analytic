# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.multi
    @api.depends('productions')
    def _compute_num_productions(self):
        for analytic_account in self:
            analytic_account.num_productions = len(
                analytic_account.productions)

    productions = fields.One2many(
        comodel_name="mrp.production", inverse_name="analytic_account_id")
    num_productions = fields.Integer(compute="_compute_num_productions")
