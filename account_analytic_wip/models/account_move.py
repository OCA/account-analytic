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
        help="Tracking item generating this journal entry",
    )
