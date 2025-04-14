# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Analytic Distribution Widget Rebalance",
    "summary": "Add a button to rebalance the analytic distribution back to 100%",
    "version": "17.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "category": "Analytic",
    "depends": ["analytic"],
    "assets": {
        "web.assets_backend": [
            "account_analytic_distribution_widget_rebalance/static/src/**/*",
        ],
        "web.qunit_suite_tests": [
            "account_analytic_distribution_widget_rebalance/static/tests/**/*.js",
        ],
    },
}
