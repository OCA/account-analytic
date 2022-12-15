# Copyright 2022 Le Filament
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Account move update analytic",
    "version": "14.0.1.0.1",
    "category": "Accounting & Finance",
    "summary": "This module allows the user to update analytic on posted moves",
    "author": "Le Filament, Moduon, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/account_move_update_analytic_view.xml",
        "views/account_move_view.xml",
        "views/account_move_line_view.xml",
    ],
    "installable": True,
}
