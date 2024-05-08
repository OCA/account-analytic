# Copyright 2023 Tecnativa - Yadier Quesada (https://www.tecnativa.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Analytic Spread by Tag",
    "version": "17.0.1.0.1",
    "author": "Miquel Alzanillas (APSL-Nagarro), Odoo Community Association (OCA)",
    "category": "Account",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account_analytic_tag"],
    "data": [
        "views/account_analytic_account_views.xml",
        "views/account_analytic_tag_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
