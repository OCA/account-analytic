# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fill_in_move_line(env):
    analytic_field = [
        (
            "analytic_account_id",
            "stock.move.line",
            "stock_move_line",
            "many2one",
            "int4",
            "stock_analytic",
        )
    ]
    openupgrade.add_fields(env, analytic_field)
    query = """
        UPDATE stock_move_line
            SET analytic_account_id = sm.analytic_account_id
            FROM stock_move sm WHERE sm.id = stock_move_line.move_id
            AND sm.analytic_account_id IS NOT NULL
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _fill_in_move_line(env)
