# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    indirect_costs_root_plan_ids = fields.Many2many(
        "account.analytic.plan",
        "res_company_indirect_costs_plan_rel",
        "company_id",
        "plan_id",
        string="Indirect Costs Analytic Plans",
        help="Analytic plans for indirect costs. "
        "All analytic accounts under these plans and their children "
        "will be considered as indirect costs.",
    )
    profit_centres_root_plan_ids = fields.Many2many(
        "account.analytic.plan",
        "res_company_profit_centres_plan_rel",
        "company_id",
        "plan_id",
        string="Profit Centres Analytic Plans",
        help="Analytic plans for profit centres. "
        "All analytic accounts under these plans and their children "
        "will be considered as profit centres.",
    )
