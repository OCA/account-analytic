# -*- coding: utf-8 -*-
# Copyright 2014 Acsone - Stéphane Bidoul <stephane.bidoul@acsone.eu>
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Analytic Distribution Required',
    'version': '10.0.1.0.0',
    'category': 'Analytic Accounting',
    'license': 'AGPL-3',
    'author': "ACSONE SA/NV, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.acsone.eu/',
    'depends': [
        'account_analytic_required',
        'account_analytic_distribution',
    ],
    'application': False,
    'installable': True,
}
