# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    user_id = fields.Many2one('res.users', string='Salesperson')

    @api.model
    def create(self, vals):
        """Adds the salesperson to the created analytic account"""
        user_id = self.env.context.get('analytic_user_id')
        if user_id:
            vals['user_id'] = user_id
        return super().create(vals)


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    account_user_id = fields.Many2one(related='account_id.user_id', store=True)
