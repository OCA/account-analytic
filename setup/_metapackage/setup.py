import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-account_analytic_required',
        'odoo11-addon-analytic_base_department',
        'odoo11-addon-analytic_tag_dimension',
        'odoo11-addon-analytic_tag_dimension_purchase_warning',
        'odoo11-addon-analytic_tag_dimension_sale_warning',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
