# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Base Department - HR Timesheet",
    "summary": "adds account_department_id to timesheets.analysis.report",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["analytic_base_department", "hr_timesheet"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/analytic_line_views.xml",
    ],
}
