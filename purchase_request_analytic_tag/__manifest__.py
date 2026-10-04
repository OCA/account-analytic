# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Request Analytic Tag",
    "version": "18.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["purchase_request", "purchase_analytic_tag"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/purchase_request_view.xml",
        "views/purchase_request_line_view.xml",
    ],
    "maintainers": ["Saran440"],
}
