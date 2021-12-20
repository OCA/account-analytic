# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pos Stock Analytic",
    "summary": """
        Allows to transmit the analytic account set on POS config from pos order to moves""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "point_of_sale",
        "stock_analytic",
        "pos_analytic_by_config",
    ],
}
