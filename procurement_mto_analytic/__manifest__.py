# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Analytic (MTO)",
    "summary": "This module sets analytic account in purchase order line from "
    "sale order analytic account",
    "version": "17.0.1.0.0",
    "category": "Analytic",
    "license": "AGPL-3",
    "author": "Tecnativa, VentorTech, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "sale_stock_analytic",
        "purchase_stock",
        "stock_analytic",
        "sale_purchase",
    ],
    "installable": True,
}
