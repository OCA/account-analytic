# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ActivityCostRule(models.Model):
    _name = "activity.cost.rule"
    _description = "Activity Cost Rule"

    name = fields.Char("Description")
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one(
        "product.product",
        "Activity Product",
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Cost Product",
        required=True,
    )
    factor = fields.Float("Qty. Factor", default=1)
    standard_price = fields.Float(
        related="product_id.standard_price",
        readonly=False,
    )

    @api.model
    def create(self, vals):
        new = super().create(vals)
        new.parent_id.onchange_for_standard_price()
        return new
