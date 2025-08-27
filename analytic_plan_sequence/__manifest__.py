# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Analytic Plan Sequence",
    "summary": "Control analytic plan display order with a sequence",
    "version": "16.0.1.0.0",
    "category": "Analytic",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Quartile, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["analytic"],
    "data": [
        "views/analytic_plan_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "analytic_plan_sequence/static/src/components/*.esm.js",
        ],
        "web.qunit_suite_tests": [
            "analytic_plan_sequence/static/src/tests/*.esm.js",
        ],
    },
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
