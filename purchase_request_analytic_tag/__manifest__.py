# Copyright 2026 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Request Analytic Tag",
    "summary": """
        Adds analytic tags to purchase request lines and propagates them to
        purchase orders created from purchase requests.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Purchase Management",
    "depends": ["purchase_request", "purchase_analytic_tag"],
    "data": [
        "views/purchase_request_line_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
    "maintainers": ["marcelsavegnago", "kaynnan"],
}
