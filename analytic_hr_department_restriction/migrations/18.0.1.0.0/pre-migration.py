# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists

column_renames = {
    "account_analytic_plan": [("department_id", "old_department_id")],
}


@openupgrade.migrate()
def migrate(env, version):
    """Rename the column to keep the old value."""
    if column_exists(env.cr, "account_analytic_plan", "department_id"):
        openupgrade.rename_columns(env.cr, column_renames)
