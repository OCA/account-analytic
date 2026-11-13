{
    "name": "Account Payment Analytic",
    "summary": "Add an analytic distribution on payments and push it to the "
    "receivable/payable journal item",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Spearhead, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Accounting",
    "depends": ["account"],
    "data": [
        "views/account_payment_views.xml",
        "wizard/account_payment_register_views.xml",
    ],
    "installable": True,
}
