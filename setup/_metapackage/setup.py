import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_analytic_required>=16.0dev,<16.1dev',
        'odoo-addon-account_analytic_tag>=16.0dev,<16.1dev',
        'odoo-addon-account_analytic_tag_distribution>=16.0dev,<16.1dev',
        'odoo-addon-account_move_update_analytic>=16.0dev,<16.1dev',
        'odoo-addon-product_analytic>=16.0dev,<16.1dev',
        'odoo-addon-purchase_analytic>=16.0dev,<16.1dev',
        'odoo-addon-purchase_stock_analytic>=16.0dev,<16.1dev',
        'odoo-addon-stock_analytic>=16.0dev,<16.1dev',
        'odoo-addon-stock_picking_analytic>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
