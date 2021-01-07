# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ActivityCostRule(models.Model):
    _name = "activity.cost.rule"
    _description = "Activity Cost Rule"

    name = fields.Char("Name", required=True)
    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    active = fields.Boolean(default=True)

    activity_product_id = fields.Many2one("product.product", "Activity Product")
    has_project = fields.Boolean(name="Is related to a Project")

    cost_type_product_id = fields.Many2one(
        "product.product",
        string="Cost Type Product",
        domain=[("type", "in", ["consu", "service"])],
    )
    factor = fields.Float("Factor", default=1)
