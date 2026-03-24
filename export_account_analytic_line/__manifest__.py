# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Export Account Analytic Line",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "This module extends the functionality of "
    "the account analytic line list view "
    "and allow you to export the selected lines",
    "author": "Heliconia Solutions Pvt. Ltd., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["report_xlsx_helper", "account_analytic_tag"],
    "data": [
        "report/account_analytic_line_xlsx.xml",
        "views/account_analytic_line_views.xml",
        "views/menuitems.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["Bhavesh Heliconia"],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}
