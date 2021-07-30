# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class AccountAnalytic(models.Model):
    """
    An Analytic Account can have one or more related Tracking Items.
    Depending on the extensions installed, you might have
    Tracking Items per Task or per Manufacturing Order.
    """

    _inherit = "account.analytic.account"

    analytic_tracking_item_ids = fields.One2many(
        "account.analytic.tracking.item",
        "analytic_id",
        string="Tracking Items",
    )
