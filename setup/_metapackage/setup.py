import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-account_analytic_asset',
        'odoo11-addon-account_analytic_default_account',
        'odoo11-addon-account_analytic_distribution',
        'odoo11-addon-account_analytic_parent',
        'odoo11-addon-account_analytic_required',
        'odoo11-addon-account_analytic_sequence',
        'odoo11-addon-account_move_analytic_recreate',
        'odoo11-addon-analytic_base_department',
        'odoo11-addon-analytic_partner',
        'odoo11-addon-analytic_product_category',
        'odoo11-addon-analytic_tag_dimension',
        'odoo11-addon-analytic_tag_dimension_purchase_warning',
        'odoo11-addon-analytic_tag_dimension_sale_warning',
        'odoo11-addon-mrp_analytic',
        'odoo11-addon-pos_analytic_by_config',
        'odoo11-addon-procurement_mto_analytic',
        'odoo11-addon-product_analytic',
        'odoo11-addon-stock_analytic',
        'odoo11-addon-stock_inventory_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
