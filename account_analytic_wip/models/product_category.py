# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    # property_wip_account_id = fields.Many2one(
    #     "account.account",
    #     "WIP Account",
    #     company_dependent=True,
    #     domain="[('company_id', '=', allowed_company_ids[0]), "
    #     "('deprecated', '=', False)]",
    #     check_company=True,
    # )
    property_variance_account_id = fields.Many2one(
        "account.account",
        "Variance Account",
        company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), "
        "('deprecated', '=', False)]",
        check_company=True,
    )
