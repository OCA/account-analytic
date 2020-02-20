# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AnalyticLine(models.Model):
    """Added Product Category in Analytic Account Line."""

    _inherit = "account.analytic.line"

    product_category_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
        related='product_id.categ_id',
        store=True,
        readonly=True)
