# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Analytic Distribution",
    "summary": "Distribute incoming/outcoming account moves to several "
               "analytic accounts",
    "version": "10.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_view.xml",
        "views/account_analytic_distribution_view.xml",
        "views/account_move_view.xml",
        "views/account_invoice_view.xml",
        "views/account_move_line_view.xml",
    ],
    "installable": True,
    "application": False,
}
