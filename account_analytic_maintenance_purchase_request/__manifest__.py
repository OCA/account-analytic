{
    "name": "Account Analytic Maintenance Purchase Request",
    "version": "18.0.1.0.0",
    "summary": """ Propagate analytic distribution from maintenance
    equipment to purchase request""",
    "author": "Spearhead, Ricardo MC, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Analytic Accounting",
    "license": "AGPL-3",
    "depends": [
        "account_analytic_maintenance",
        "maintenance_request_purchase",
        "purchase_analytic",
    ],
    "data": ["views/maintenance_request_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
