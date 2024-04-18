# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    # In case you come from a previous version, reuse the security group, and avoid
    # to crash due to 2 groups with the same name.
    cr.execute(
        """UPDATE ir_model_data
        SET module='account_analytic_tag'
        WHERE module='analytic' and name='group_analytic_tags'
        """
    )
