# Copyright 2025-2026 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models
from odoo.fields import Domain
from odoo.tools import config


class IrAccess(models.Model):
    _inherit = "ir.access"

    @api.model
    def _get_analytic_department_ids(self):
        """Get departments of all employees in the user's companies."""
        user = self.env.user
        # We need to get all possible employees of the user in any company (even
        # if not defined in allowed_company_ids).
        # Example of use case:
        # - User: Company A + Company B
        # - Employee: Company A
        # - Department: Without company
        # - Plan: Wihout company + Department
        # - Purchase Order: Company A + Plan + Department
        # - If the user accesses the purchase order only with company A, he/she
        # should be able to see the plan and/or the analytical accounts.
        # Note: We need to override employee_ids so that when we pass it the
        # allowed_company_ids context it will return the appropriate value.
        user.invalidate_recordset(["employee_ids"])
        user = user.with_context(allowed_company_ids=user.company_ids.ids)
        return user.employee_ids.department_id.ids

    @api.model
    def _get_analytic_department_domain(self):
        """Inject extra domain for restricting plans and analytical accounts when the
        user has the group 'Analytic Accounting'.
        """
        user = self.env.user
        group1 = "base.group_user"
        group2 = "analytic.group_analytic_accounting"
        group3 = "analytic_hr_department_restriction.group_analytic_accounting_without_department"  # noqa: E501
        group4 = "account.group_account_invoice"
        test_condition = not config["test_enable"] or self.env.context.get(
            "test_analytic_hr_department_restriction"
        )
        if (
            self.env.su
            or not user.has_group(group1)
            or user.has_group(group4)
            or not test_condition
        ):
            return Domain.TRUE
        if not user.has_group(group2):
            return Domain.FALSE
        domain = Domain(
            "department_ids", "child_of", self._get_analytic_department_ids()
        )
        if user.has_group(group3):
            domain |= Domain("department_ids", "=", False)
        return domain

    @api.model
    def _eval_context(self):
        result = super()._eval_context()
        result["analytic_department_domain"] = self._get_analytic_department_domain()
        return result

    def _get_access_context(self):
        yield from super()._get_access_context()
        user = self.env.user
        employee = user.employee_id
        # The access domain depends on the current employee and department.
        yield employee.id
        yield employee.department_id.id
        # The resulting domain also depends on these group memberships.
        yield user.has_group("account.group_account_invoice")
        yield user.has_group(
            "analytic_hr_department_restriction."
            "group_analytic_accounting_without_department"
        )
