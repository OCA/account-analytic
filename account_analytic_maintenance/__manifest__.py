{
    "name": "Account Analytic Maintenance",
    "version": "18.0.1.0.0",
    "summary": """ Adds analytic distribution to maintenance equipment """,
    "author": "Spearhead, Ricardo MC, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Analytic Accounting",
    "license": "AGPL-3",
    "depends": [
        "maintenance",
        "analytic",
    ],
    "data": [
        "views/maintenance_equipment_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
