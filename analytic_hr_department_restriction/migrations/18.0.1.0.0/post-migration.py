# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    """Set the department_id value in the project company."""
    if not column_exists(env.cr, "account_analytic_plan", "old_department_id"):
        return
    openupgrade.convert_to_company_dependent(
        env, "account.analytic.plan", "old_department_id", "department_id"
    )
