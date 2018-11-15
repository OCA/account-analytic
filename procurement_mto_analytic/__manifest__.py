# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Analytic (MTO)',
    'summary': 'This module sets analytic account in purchase order line from '
               'sale order analytic account',
    'version': '11.0.1.0.0',
    'category': 'Analytic',
    'license': 'AGPL-3',
    'author': "VentorTech, "
              "Odoo Community Association (OCA)",
    'website': 'https://ventor.tech/',
    'depends': [
        'sale',
        'sale_stock',
        'purchase',
    ],
    'installable': True,
}
