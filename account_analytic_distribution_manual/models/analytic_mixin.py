# Copyright 2024 Tecnativa - Carlos Lopez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    manual_distribution_id = fields.Many2one("account.analytic.distribution.manual")
    analytic_distribution_import = fields.Json(
        compute="_compute_analytic_distribution_import",
        inverse="_inverse_analytic_distribution_import",
        readonly=False,
        string="Analytic distribution (importable)",
        help="Defining this field, it will set the analytical distribution in JSON "
        "format, but using the analytic accounts names as keys of the dictionary, so it "
        "eases the human input.",
    )

    @api.depends("analytic_distribution")
    def _compute_analytic_distribution_import(self):
        aa_model = self.env["account.analytic.account"]
        for item in self:
            data = {}
            distribution = item.analytic_distribution or {}
            for key in list(distribution.keys()):
                aa_record = aa_model.browse(int(key))
                data[aa_record.name] = distribution[key]
            item.analytic_distribution_import = data

    def _inverse_analytic_distribution_import(self):
        """Convert the json to the appropriate value of analytic_distribution."""
        aa_model = self.env["account.analytic.account"]
        for item in self:
            company = (
                item.company_id if "company_id" in item._fields else self.env.company
            )
            base_domain = [("company_id", "in", company.ids + [False])]
            data = {}
            new_distribution = item.analytic_distribution_import or {}
            for key in list(new_distribution.keys()):
                domain = base_domain + [("name", "=", key)]
                aa_record = aa_model.search(
                    domain,
                    limit=1,
                )
                if aa_record:
                    data[aa_record.id] = new_distribution[key]
            item.analytic_distribution = data
