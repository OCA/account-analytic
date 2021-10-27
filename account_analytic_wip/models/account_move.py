# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountMove(models.Model):
    """
    Journal Entries are linked to Tracking Items
    to allow computing the actual amounts
    """

    _inherit = "account.move"

    analytic_tracking_item_id = fields.Many2one(
        "account.analytic.tracking.item",
        string="Tracking Item",
        ondelete="set null",
        help="Tracking item generating this journal entry",
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # TODO: DROP
    # clear_wip_account_id = fields.Many2one(
    #     "account.account",
    #     string="Clear WIP Account",
    #     help="Counterpart account used when this WIP item is cleared",
    # )
    is_wip = fields.Boolean(compute="_compute_is_wip_account")

    @api.depends("product_id.categ_id.property_wip_account_id")
    def _compute_is_wip_account(self):
        """
        Identify WIP journal items.
        This is needed to compute total WIP balance
        and create WIP clearing journal entries.

        It is a WIP item if any of:
        - Has a Destination Location with Input account(from related Stock Move)
        - Has a Source Location with Output account (from related Stock Move)
        - Has a Product Category with a WIP Account set
        """
        for line in self:
            if line.product_id:
                wip_acc = (
                    line.move_id.stock_move_id.location_dest_id.valuation_in_account_id
                    or line.move_id.stock_move_id.location_id.valuation_out_account_id
                    or line.product_id.categ_id.property_wip_account_id
                )
                line.is_wip = wip_acc and wip_acc == line.account_id
            else:
                line.is_wip = False
