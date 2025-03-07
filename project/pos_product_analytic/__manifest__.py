{
    'name': "POS Product Analytic",
    'summary': """Use analytic account defined on
                  product for POS orders""",
    'author': 'Trobz',
    'website': "https://trobz.com",
    'category': 'Point Of Sale, Accounting',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
        'product_analytic',
    ],
    'data': [
        'data/ir_cron.xml',
    ],
}
