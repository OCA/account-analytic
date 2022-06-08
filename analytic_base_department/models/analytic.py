from odoo import api, fields, models


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    department_id = fields.Many2one("hr.department")


class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def _default_department(self):
        department_id = False
        employee = self.env.user.employee_ids
        if employee and employee[0].department_id:
            department_id = employee[0].department_id.id
        return department_id

    department_id = fields.Many2one(
        comodel_name="hr.department",
        default=lambda self: self._default_department(),
        help="User's related department",
    )
    account_department_id = fields.Many2one(
        comodel_name="hr.department",
        related="account_id.department_id",
        string="Account Department",
        store=True,
        readonly=True,
        help="Account's related department",
    )
