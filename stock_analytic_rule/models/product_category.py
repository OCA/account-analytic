# Copyright 2025 Bernat Obrador APSL-Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    avg_price = fields.Float(
        string="Average Price",
        digits=(16, 2),
        help="""This field is used to store the average price of the products""",
    )
    avg_weight = fields.Float(
        string="Average Weight",
        digits=(16, 2),
        help="""This field is used to store the average weight of the products""",
    )

    custom_computation_for_internal_moves = fields.Boolean(
        string="Custom Computation for Internal Moves",
        help="""If checked, the average price and weight for
        internal moves will be used instead of the standard ones""",
    )

    avg_price_for_internal_moves = fields.Float(
        string="Average Price for Internal Moves",
        digits=(16, 2),
        help="""This field is used to store the average price of
        the products for internal moves""",
    )
    avg_weight_for_internal_moves = fields.Float(
        string="Average Weight for Internal Moves",
        digits=(16, 2),
        help="""This field is used to store the average weight of
        the products for internal moves""",
    )

    supplement = fields.Float(
        digits=(16, 2),
        help="""This field is used to supplement the cost of the product""",
    )
