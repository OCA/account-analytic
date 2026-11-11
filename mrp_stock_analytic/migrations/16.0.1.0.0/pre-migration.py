# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_160


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "mrp_production", "analytic_account_id"):
        return
    m2m_rel = "account_analytic_tag_mrp_production_rel"
    has_tags = openupgrade.table_exists(env.cr, m2m_rel)
    openupgrade_160.fill_analytic_distribution(
        env,
        "mrp_production",
        m2m_rel=has_tags and m2m_rel,
        m2m_column1=has_tags and "mrp_production_id",
    )
