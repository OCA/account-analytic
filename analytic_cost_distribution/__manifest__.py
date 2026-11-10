# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Cost Distribution",
    "summary": "Distribute indirect costs to profit centres",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "license": "AGPL-3",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "account",
        "analytic",
        "hr_timesheet",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/res_config_settings_views.xml",
        "views/indirect_cost_distribution_model_views.xml",
        "views/cost_distribution_operation_views.xml",
        "views/account_analytic_line_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
