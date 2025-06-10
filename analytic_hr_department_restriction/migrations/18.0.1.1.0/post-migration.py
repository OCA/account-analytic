# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    if column_exists(env.cr, "account_analytic_account", "department_id"):
        openupgrade.m2o_to_x2m(
            env.cr,
            env["account.analytic.account"],
            "account_analytic_account",
            "department_ids",
            "department_id",
        )
    if column_exists(env.cr, "account_analytic_plan", "department_id"):
        openupgrade.m2o_to_x2m(
            env.cr,
            env["account.analytic.plan"],
            "account_analytic_plan",
            "department_ids",
            "department_id",
        )
