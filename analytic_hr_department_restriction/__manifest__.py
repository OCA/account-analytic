# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Analytic distributions restriction per HR department",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "version": "18.0.1.1.0",
    "depends": ["account", "hr"],
    "license": "AGPL-3",
    "category": "Account",
    "installable": True,
    "maintainers": ["victoralmau"],
    "data": [
        "security/groups.xml",
        "views/account_analytic_account_views.xml",
        "views/account_analytic_plan_views.xml",
    ],
}
