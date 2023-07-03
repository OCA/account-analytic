# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        company_dependent=True,
        string="Customer Analytic Account",
        help="Default Analytic Account used for Invoices / Credit Notes.",
    )

    property_supplier_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        company_dependent=True,
        string="Vendor Analytic Account",
        help="Default Analytic Account used for Vendor Bills / Vendor Refund.",
    )

    def get_partner_analytic_accounts(self, company_id=False):
        self.ensure_one()
        if not company_id:
            company_id = self.env.context.get("company_id")
        self = self.with_company(company_id)
        return {
            "income": self.property_analytic_account_id,
            "expense": self.property_supplier_analytic_account_id,
        }

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + [
            "property_analytic_account_id",
            "property_supplier_analytic_account_id",
        ]
