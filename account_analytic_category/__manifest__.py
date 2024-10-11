# Copyright: Henrik Norlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Analytic Categories",
    "version": "16.0.1.0.0",
    "author": "Henrik Norlin, Odoo Community Association (OCA)",
    "category": "Account",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "account_move_line_analytic_account_ids",
    ],
    "data": [
        "security/account_analytic_category_security.xml",
        "security/ir.model.access.csv",
        "views/account_analytic_account_views.xml",
        "views/account_analytic_category_views.xml",
        "views/account_move_views.xml",
        "views/account_move_line_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
