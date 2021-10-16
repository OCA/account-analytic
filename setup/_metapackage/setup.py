import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_analytic_parent',
        'odoo14-addon-account_analytic_required',
        'odoo14-addon-account_analytic_wip',
        'odoo14-addon-analytic_activity_based_cost',
        'odoo14-addon-analytic_base_department',
        'odoo14-addon-analytic_partner',
        'odoo14-addon-analytic_tag_dimension',
        'odoo14-addon-analytic_tag_dimension_enhanced',
        'odoo14-addon-mrp_analytic',
        'odoo14-addon-mrp_analytic_child_mo',
        'odoo14-addon-mrp_analytic_sale_project',
        'odoo14-addon-stock_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
