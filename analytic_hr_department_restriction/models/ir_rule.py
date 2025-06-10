# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, tools
from odoo.osv import expression
from odoo.tools import config


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        """Inject extra domain for restricting plans and analytical accounts when the
        user has the group 'Analytic Accounting'.
        """
        res = super()._compute_domain(model_name, mode=mode)
        user = self.env.user
        group1 = "base.group_user"
        group2 = "analytic.group_analytic_accounting"
        group3 = "analytic_hr_department_restriction.group_analytic_accounting_without_department"  # noqa: E501
        group4 = "account.group_account_invoice"
        test_condition = not config["test_enable"] or self.env.context.get(
            "test_analytic_hr_department_restriction"
        )
        if (
            model_name in ("account.analytic.account", "account.analytic.plan")
            and not self.env.su
            and user.has_group(group1)
            and not user.has_group(group4)
            and test_condition
        ):
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
            if user.has_group(group2):
                extra_domain = [
                    ("department_ids", "child_of", user.employee_ids.department_id.ids)
                ]
                if user.has_group(group3):
                    extra_domain = expression.OR(
                        [extra_domain, [("department_ids", "=", False)]]
                    )
            else:
                extra_domain = [("id", "=", 0)]
            res = expression.AND([extra_domain] + [res])
        return res
