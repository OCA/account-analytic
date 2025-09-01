# Copyright 2025 Bernat Obrador APSL-Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Analytic Rule",
    "summary": """Adds distribution rules for stock moves
    to automatically create analytic lines""",
    "version": "17.0.1.0.0",
    "author": "Odoo Community Association (OCA), APSL-Nagarro, Bernat Obrador",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "maintainers": ["BernatObrador"],
    "depends": ["stock", "account", "analytic"],
    "data": [
        "security/analytic_security.xml",
        "security/ir.model.access.csv",
        "views/account_analytic_line_views.xml",
        "views/product_category_views.xml",
        "views/stock_analytic_model.xml",
    ],
    "installable": True,
}
