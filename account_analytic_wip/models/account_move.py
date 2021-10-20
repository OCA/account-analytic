# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


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


# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     clear_wip_account_id = fields.Many2one(
#         "account.account",
#         string="Clear WIP Account",
#         help="Counterpart account used when this WIP item is cleared",
#     )
