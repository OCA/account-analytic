import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_analytic_distribution',
        'odoo9-addon-account_analytic_no_lines',
        'odoo9-addon-account_analytic_parent',
        'odoo9-addon-account_analytic_required',
        'odoo9-addon-analytic_base_department',
        'odoo9-addon-analytic_department',
        'odoo9-addon-procurement_analytic',
        'odoo9-addon-purchase_analytic_distribution',
        'odoo9-addon-sale_analytic_distribution',
        'odoo9-addon-stock_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
