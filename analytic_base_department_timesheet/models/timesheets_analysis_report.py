# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    account_department_id = fields.Many2one(
        comodel_name="hr.department",
        readonly=True,
        help="Account's related department",
    )

    @api.model
    def _select(self):
        return (
            super()._select()
            + """,
                A.account_department_id AS account_department_id
        """
        )
