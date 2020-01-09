# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class Picking(models.Model):
    _inherit = "stock.picking"

    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        comodel_name='account.analytic.account',
    )

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        """ When analytic_account_id is changed, set analytic account on all moves.
        """
        for move in self.move_ids_without_package:
            move.analytic_account_id = self.analytic_account_id
