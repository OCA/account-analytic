# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class AnalyticLine(models.Model):
    """
    Analytic Lines should keep a link to the corresponding Tracking Item,
    so that it can report the corresponding WIP amounts.
    """

    _inherit = "account.analytic.line"

    analytic_tracking_item_id = fields.Many2one(
        "account.analytic.tracking.item", string="Tracking Item"
    )
