
from odoo import fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    account_department_id = fields.Many2one(
        comodel_name="hr.department",
        related="department_id",
        string="Account Department",
        store=True,
        readonly=True,
        help="Account's related department",
    )
