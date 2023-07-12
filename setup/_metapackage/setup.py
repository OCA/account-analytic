import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-account-analytic",
    description="Meta package for oca-account-analytic Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_analytic_distribution_required',
        'odoo14-addon-account_analytic_parent',
        'odoo14-addon-account_analytic_required',
        'odoo14-addon-account_analytic_sequence',
        'odoo14-addon-account_analytic_tag_default',
        'odoo14-addon-account_analytic_wip',
        'odoo14-addon-account_move_update_analytic',
        'odoo14-addon-analytic_activity_based_cost',
        'odoo14-addon-analytic_base_department',
        'odoo14-addon-analytic_partner',
        'odoo14-addon-analytic_partner_hr_timesheet',
        'odoo14-addon-analytic_tag_dimension',
        'odoo14-addon-analytic_tag_dimension_enhanced',
        'odoo14-addon-mrp_analytic',
        'odoo14-addon-mrp_analytic_child_mo',
        'odoo14-addon-mrp_analytic_sale_project',
        'odoo14-addon-pos_analytic_by_config',
        'odoo14-addon-procurement_mto_analytic',
        'odoo14-addon-product_analytic',
        'odoo14-addon-product_analytic_purchase',
        'odoo14-addon-product_analytic_sale',
        'odoo14-addon-purchase_analytic',
        'odoo14-addon-purchase_request_analytic',
        'odoo14-addon-purchase_stock_analytic',
        'odoo14-addon-sale_stock_analytic',
        'odoo14-addon-stock_analytic',
        'odoo14-addon-stock_inventory_analytic',
        'odoo14-addon-stock_picking_analytic',
        'odoo14-addon-stock_warehouse_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
