import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-account_analytic_default_account',
        'odoo10-addon-account_analytic_distribution',
        'odoo10-addon-account_analytic_distribution_required',
        'odoo10-addon-account_analytic_no_lines',
        'odoo10-addon-account_analytic_parent',
        'odoo10-addon-account_analytic_required',
        'odoo10-addon-account_analytic_sequence',
        'odoo10-addon-account_asset_analytic',
        'odoo10-addon-analytic_base_department',
        'odoo10-addon-analytic_partner',
        'odoo10-addon-analytic_partner_hr_timesheet',
        'odoo10-addon-analytic_partner_hr_timesheet_invoice',
        'odoo10-addon-analytic_tag_dimension',
        'odoo10-addon-analytic_tag_dimension_purchase_warning',
        'odoo10-addon-analytic_tag_dimension_sale_warning',
        'odoo10-addon-procurement_analytic',
        'odoo10-addon-product_analytic',
        'odoo10-addon-product_analytic_pos',
        'odoo10-addon-product_analytic_purchase',
        'odoo10-addon-purchase_procurement_analytic',
        'odoo10-addon-sale_analytic_distribution',
        'odoo10-addon-sale_procurement_analytic',
        'odoo10-addon-stock_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
