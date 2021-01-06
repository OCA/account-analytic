# Copyright 2011-2018 Camptocamp SA
# Copyright 2013 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Base Analytic Department Categorization",
    "summary": "Add relationshet between Analytic and Department",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Daniel Reis, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Projects & Services",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account", "hr"],
    "data": ["views/analytic.xml", "views/hr_department_views.xml"],
    "installable": True,
}
