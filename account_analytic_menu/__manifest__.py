{
    "name": "Account Analytic Menu",
    "version": "16.0.1.0.0",
    "summary": """Add a menu to structure the analytic in a more
    user-friendly way""",
    "category": "Analytic Accounting",
    "license": "AGPL-3",
    "author": """Lansana Barry, Miquel Alzanillas, Miquel Pascual,
    Odoo Community Association (OCA)""",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["analytic", "account"],
    "data": [
        "views/account_menuitem.xml",
    ],
    "installable": True,
    "maintainers": ["mpascuall"],
}
