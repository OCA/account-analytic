# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if version and version <= "10.0.1.0.0":
        openupgrade.rename_xmlids(
            env.cr,
            [
                (
                    "account_analytic_no_lines.hide_analytic_entries",
                    "account_analytic_no_lines.show_analytic_entries",
                )
            ],
        )
