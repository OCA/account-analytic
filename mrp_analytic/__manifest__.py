# Copyright 2015 ForgeFlow - Jordi Ballester Alomar
# Copyright 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Analytic for manufacturing",
    "summary": "Adds the analytic account to the production order",
    "version": "13.0.1.0.0",
    "category": "Manufacturing",
    "author": "ForgeFlow, "
    "Antiun Ingeniería, "
    "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
    "José L. Sandoval A., "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": ["mrp", "analytic"],
    "data": ["views/mrp_view.xml", "views/analytic_account_view.xml"],
    "installable": True,
}
