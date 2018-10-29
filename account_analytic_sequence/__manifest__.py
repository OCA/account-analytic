# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Analytic Sequence',
    'summary': """
        Restore the analytic account sequence""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account_analytic',
    'depends': [
        'analytic',
    ],
    'data': [
        'data/sequence.xml',
    ],
}
