# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"

    analytic_distribution_model_ids = fields.One2many(
        "account.analytic.distribution.model",
        "product_categ_id",
        string="Analytic Distribution Models",
    )
