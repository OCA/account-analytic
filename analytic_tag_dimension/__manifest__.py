# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Analytic Accounts Dimensions",
    'summary': "Group Analytic Entries by Dimensions",
    "version": "12.0.2.0.0",
    "license": "AGPL-3",
    "author": "PESOL, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        'analytic',
        'account',
    ],
    "data": [
        'views/analytic_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo": [
        'demo/analytic_demo.xml',
    ],
    "uninstall_hook": "uninstall_hook",
}
