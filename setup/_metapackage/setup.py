import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_analytic_default_purchase',
        'odoo12-addon-account_analytic_distribution_required',
        'odoo12-addon-account_analytic_line_name_text',
        'odoo12-addon-account_analytic_parent',
        'odoo12-addon-account_analytic_required',
        'odoo12-addon-account_analytic_root',
        'odoo12-addon-account_analytic_sequence',
        'odoo12-addon-account_move_analytic_recreate',
        'odoo12-addon-analytic_base_department',
        'odoo12-addon-analytic_partner',
        'odoo12-addon-analytic_partner_hr_timesheet',
        'odoo12-addon-analytic_product_category',
        'odoo12-addon-analytic_tag_dimension',
        'odoo12-addon-analytic_tag_dimension_enhanced',
        'odoo12-addon-analytic_tag_dimension_purchase_warning',
        'odoo12-addon-mrp_analytic',
        'odoo12-addon-pos_analytic_by_config',
        'odoo12-addon-procurement_mto_analytic',
        'odoo12-addon-product_analytic',
        'odoo12-addon-purchase_analytic',
        'odoo12-addon-purchase_request_analytic',
        'odoo12-addon-stock_analytic',
        'odoo12-addon-stock_inventory_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
