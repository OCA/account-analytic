# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountAnalytic(models.Model):
    """
    An Analytic Account can have one or more related Tracking Items.
    Depending on the extensions installed, you might have
    Tracking Items per Task or per Manufacturing Order.
    """

    _inherit = "account.analytic.account"

    analytic_tracking_item_ids = fields.One2many(
        "account.analytic.tracking.item", "analytic_id", string="Tracking Items"
    )

    @api.model
    def create(self, vals):
        """
        A default Tracking Item is automatically created.
        It will collect Atual Amounts not linked to a specific Tracking Item.
        """
        new = super().create(vals)
        self.env["account.analytic.tracking.item"].create({"analytic_id": new.id})
