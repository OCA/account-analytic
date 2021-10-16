import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_analytic_plan_required',
        'odoo8-addon-account_analytic_project',
        'odoo8-addon-account_analytic_required',
        'odoo8-addon-account_asset_analytic',
        'odoo8-addon-analytic_multicurrency',
        'odoo8-addon-analytic_partner',
        'odoo8-addon-analytic_partner_hr_timesheet',
        'odoo8-addon-analytic_partner_hr_timesheet_invoice',
        'odoo8-addon-mrp_analytic',
        'odoo8-addon-pos_analytic_by_config',
        'odoo8-addon-procurement_analytic',
        'odoo8-addon-product_analytic',
        'odoo8-addon-purchase_procurement_analytic',
        'odoo8-addon-stock_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
