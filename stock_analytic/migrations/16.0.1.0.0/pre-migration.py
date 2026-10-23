# Copyright 2026 Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_160


@openupgrade.migrate()
def migrate(env, version):
    for table in ("stock_move", "stock_move_line", "stock_scrap"):
        if openupgrade.column_exists(env.cr, table, "analytic_account_id"):
            openupgrade_160.fill_analytic_distribution(env, table)
