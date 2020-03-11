# Copyright 2020 Druidoo - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Convert analytic_policy to property_analytic_policy
    openupgrade.convert_to_company_dependent(
        env=env,
        model_name="account.account.type",
        origin_field_name="analytic_policy",
        destination_field_name="property_analytic_policy",
    )
