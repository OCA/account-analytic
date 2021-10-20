# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    original_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        help="Technical field. Use to store the value of"
        "analytic_account_id if there is no lines",
    )
    analytic_account_id = fields.Many2one(
        compute="_compute_analytic_account_id",
        inverse="_inverse_analytic_account_id",
        comodel_name="account.analytic.account",
        string="Analytic Account",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "waiting": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "assigned": [("readonly", False)],
        },
        store=True,
    )

    @api.depends("move_ids_without_package.analytic_account_id")
    def _compute_analytic_account_id(self):
        """
        Get analytic account from first move and put it on picking
        """
        for picking in self:
            analytic_account = picking.original_analytic_account_id
            if picking.move_ids_without_package:
                analytic_account = picking.move_ids_without_package[
                    0
                ].analytic_account_id
                if any(
                    move.analytic_account_id != analytic_account
                    for move in picking.move_ids_without_package
                ):
                    analytic_account = analytic_account.browse()
            picking.analytic_account_id = analytic_account

    def _inverse_analytic_account_id(self):
        """
        If anaytic account is set on picking, write it on all moves
        """
        for picking in self:
            if picking.analytic_account_id:
                picking.move_ids_without_package.write(
                    {"analytic_account_id": picking.analytic_account_id.id}
                )
            picking.original_analytic_account_id = picking.analytic_account_id
