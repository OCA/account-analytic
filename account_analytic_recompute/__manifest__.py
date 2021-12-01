# Copyright 2021 Trescloud - Adrian Lima
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Account Analytic Recompute",
    "version": "14.0.0.0.0",
    "category": "Analytic Accounting",
    "license": "LGPL-3",
    "author": "Trescloud, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "account"
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'wizards/wizard_change_account_analytic.xml'
    ],
    "installable": True,
}
