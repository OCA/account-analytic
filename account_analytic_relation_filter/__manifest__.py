# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Analytic Relation Filter",
    "summary": "Filter analytic distribution options based on analytic account relations",
    "version": "16.0.1.0.0",
    "category": "Analytic",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Quartile, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["analytic"],
    "data": [
        "security/ir.model.access.csv",
        "views/analytic_account_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_analytic_relation_filter/static/src/component/*.esm.js",
        ],
        "web.qunit_suite_tests": [
            "account_analytic_relation_filter/static/tests/*.esm.js",
        ],
    },
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
