# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Analytic Accounts Dimensions Enhanced",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["analytic_tag_dimension"],
    "data": [
        "security/ir.model.access.csv",
        "views/analytic_view.xml",
        "views/account_move_view.xml",
    ],
    "installable": True,
}
