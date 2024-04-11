# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrExpense(models.Model):

    _inherit = "hr.expense"

    @api.depends("employee_id")
    def _compute_analytic_distribution(self):
        ret = super()._compute_analytic_distribution()

        for rec in self:
            # add analytic account of employee's department in distribution
            if rec.employee_id:
                analytic_acc = rec.employee_id.department_id.account_analytic_id
                if analytic_acc:
                    distribution = rec.analytic_distribution or {}
                    distribution[str(analytic_acc.id)] = 100.0
                    rec.analytic_distribution = distribution

        return ret
