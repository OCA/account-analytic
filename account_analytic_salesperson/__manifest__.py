# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Account Analytic Salesperson",
    "summary": "Propagate salesperson from sale order to analytic account",
    "version": "11.0.1.0.0",
    "category": "Analytic Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "views/analytic_account.xml",
    ],
}
