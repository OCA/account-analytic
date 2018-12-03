import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_analytic_parent',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
