# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line AS aal
        SET manual_distribution_id = aml.manual_distribution_id
        FROM account_move_line AS aml
        WHERE aal.move_line_id = aml.id
        AND aml.manual_distribution_id IS NOT NULL
        AND aal.manual_distribution_id IS NULL
        """,
    )
