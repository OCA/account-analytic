# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    account_department_id = fields.Many2one(
        comodel_name="hr.department",
        readonly=True,
    )

    def _select(self):
        return super()._select() + ", A.account_department_id AS account_department_id"
