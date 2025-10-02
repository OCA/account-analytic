# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "analytic.mixin"]

    income_analytic_distribution = fields.Json()
    expense_analytic_distribution = fields.Json()

    def _get_product_analytic_accounts(self):
        self.ensure_one()
        return {
            "income": self.income_analytic_distribution
            or self.categ_id.income_analytic_distribution,
            "expense": self.expense_analytic_distribution
            or self.categ_id.expense_analytic_distribution,
        }
