# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Account Analytic Default Account',
    'version': '11.0.1.0.0',
    'category': 'Analytic Accounting',
    'license': 'AGPL-3',
    'author': "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/account-analytic',
    'depends': [
        'account',
        'analytic',
        'account_analytic_default'
    ],
    'data': [
        'views/account_analytic_default_account_view.xml'
    ],
    'installable': True,
}
