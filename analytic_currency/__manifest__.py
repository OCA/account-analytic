# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Analytic Accounting: Currency',
    'version': '12.0.1.0.0',
    'category': 'Analytic Accounting',
    'website': 'https://github.com/OCA/account-analytic',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Configurable analytic account currency.',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_analytic_account.xml',
        'views/account_analytic_line.xml',
    ]
}
