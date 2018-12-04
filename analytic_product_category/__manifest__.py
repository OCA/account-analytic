# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Base Analytic Product Category Categorization",
    "summary": "Filter and Group Analytic Entries by Product Category",
    "category": "Generic Modules/Accounting",
    "version": "12.0.1.0.0",
    "author": "PESOL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account"],
    "data": ["views/analytic.xml"],
    'pre_init_hook': 'pre_init_hook',
    "installable": True,
}
