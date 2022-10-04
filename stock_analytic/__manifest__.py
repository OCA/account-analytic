# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Analytic",
    "summary": "Adds an analytic account in stock move",
    "version": "12.0.1.0.1",
    "author": "Julius Network Solutions, "
              "ClearCorp, OpenSynergy Indonesia, "
              "Hibou Corp., "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": [
        "stock_account",
        "analytic",
    ],
    "data": [
        "views/stock_move_views.xml",
    ],
    'installable': True,
}
