# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class AccountAnalyticApplicability(models.Model):
    _inherit = "account.analytic.applicability"

    product_ids = fields.Many2many(
        "product.product",
        "account_analytic_plan_applicability_product",
        "applicability_id",
        "product_id",
        string="Products",
    )

    def _get_score(self, **kwargs):
        result = super()._get_score(**kwargs)
        if result >= 0 and self.product_ids:
            if kwargs.get("product") in self.product_ids.ids:
                result += 1
            else:
                result = -1
        return result
