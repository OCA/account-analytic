# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, exceptions, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_wip_journal_id = fields.Many2one(
        "account.journal",
        "WIP Journal",
        company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0])]",
        check_company=True,
        help="When doing automated WIP valuation, this is the Accounting Journal "
        "in which entries will be automatically posted.",
    )
    property_variance_account_id = fields.Many2one(
        "account.account",
        "Variance Account",
        company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), "
        "('deprecated', '=', False)]",
        check_company=True,
    )

    @api.constrains(
        "property_wip_journal_id",
        "property_variance_account_id",
    )
    def _constrains_wip_config(self):
        for categ in self:
            configs = [
                categ.property_wip_journal_id,
                categ.property_variance_account_id,
            ]
            if any(configs) and not all(configs):
                raise exceptions.ValidationError(
                    _(
                        "Then configuring costing, a Journal "
                        " and account for Consumption,"
                        " WIP and Variance must be provided. "
                        "Check the configuration in Category %s."
                    )
                    % categ.display_name
                )
