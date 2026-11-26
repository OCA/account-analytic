from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    """Expose account_department_id on the timesheets reporting SQL view.

    hr_timesheet's own report search view (a "primary" view on this model)
    inherits its arch from analytic.view_account_analytic_line_filter, the
    same shared ancestor this module extends with account_department_id.
    Without this field existing here too, that combination fails validating
    as soon as both modules are installed together.
    """

    _inherit = "timesheets.analysis.report"

    account_department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Account Department",
        readonly=True,
    )

    @api.model
    def _select(self):
        return super()._select() + ", A.account_department_id AS account_department_id"
