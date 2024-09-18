# Copyright 2023 APSL - Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Analytic Organization",
    "summary": """Adds organization field on the partner so you can use it on your analytic""",
    "version": "16.0.1.0.0",
    "category": "Analytic Accounting",
    "license": "AGPL-3",
    "author": "Miquel Pascual, Bernat Obrador, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["analytic", "contacts", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/account_analytic_line.xml",
        "views/account_move_line.xml",
        "views/account_analytic_organization.xml",
    ],
    "installable": True,
}
