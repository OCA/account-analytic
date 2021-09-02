# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_cost_type = fields.Boolean(string="Is Cost Driver")


class Product(models.Model):
    _inherit = "product.product"

    activity_cost_ids = fields.One2many(
        "activity.cost.rule",
        "parent_id",
        string="Activity Costs",
        help="This product will also generate analytic items for these Activity Costs",
    )

    @api.constrains("is_cost_type", "activity_cost_ids")
    def constrains_is_cost_type(self):
        for product in self:
            if not product.is_cost_type and product.activity_cost_ids:
                raise exceptions.ValidationError(
                    _("Can't have Activity Costs set if it is not a Cost Driver.")
                )

    @api.onchange("activity_cost_ids")
    def onchange_for_standard_price(self):
        "Rollup Activity Costs to parent Cost Type"
        for product in self.filtered("is_cost_type"):
            if product.type in ["consu", "service"]:
                product.standard_price = sum(
                    x.standard_price * x.factor
                    for x in product.sudo().activity_cost_ids
                )
