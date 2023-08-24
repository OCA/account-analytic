# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Tag Distribution",
    "version": "16.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "category": "Account",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account_analytic_tag"],
    "license": "AGPL-3",
    "data": [
        "views/account_analytic_tag_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "maintainers": ["victoralmau"],
}
