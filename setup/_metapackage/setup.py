import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_analytic_parent',
        'odoo13-addon-account_analytic_required',
        'odoo13-addon-analytic_base_department',
        'odoo13-addon-analytic_tag_dimension',
        'odoo13-addon-analytic_tag_dimension_sale_warning',
        'odoo13-addon-mrp_analytic',
        'odoo13-addon-procurement_mto_analytic',
        'odoo13-addon-product_analytic',
        'odoo13-addon-purchase_analytic',
        'odoo13-addon-stock_analytic',
        'odoo13-addon-stock_inventory_analytic',
        'odoo13-addon-stock_landed_costs_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
