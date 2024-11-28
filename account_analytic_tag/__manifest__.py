# Copyright 2023 Tecnativa - Yadier Quesada (https://www.tecnativa.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Analytic Tag",
    "version": "18.0.1.1.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "category": "Account",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account", "analytic"],
    "data": [
        "security/analytic_security.xml",
        "security/ir.model.access.csv",
        "views/account_analytic_line_views.xml",
        "views/account_analytic_tag_views.xml",
        "views/account_move_line_views.xml",
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
