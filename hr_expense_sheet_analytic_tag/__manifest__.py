# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Hr Expense Sheet Analytic Tag",
    "version": "19.0.1.0.2",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["hr_expense_sheet", "hr_expense_analytic_tag"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/hr_expense_sheet_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
