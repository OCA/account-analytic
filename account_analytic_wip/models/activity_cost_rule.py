# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ActivityCostRule(models.Model):
    _name = "activity.cost.rule"
    _description = "Activity Cost Rule"

    name = fields.Char("Description")
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one("product.product", "Activity Product")
    product_id = fields.Many2one(
        "product.product",
        string="Cost Type Product",
        domain=[("is_cost_type", "=", True)],
    )
    factor = fields.Float("Qty. Factor", default=1)
    standard_price = fields.Float(
        related="product_id.standard_price",
        readonly=False,
    )
