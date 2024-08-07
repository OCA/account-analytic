# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api, tools


def post_init_hook(cr, registry):
    if tools.table_exists(cr, "account_analytic_tag"):
        env = api.Environment(cr, SUPERUSER_ID, {})
        sql = """
        WITH counted_tags AS (
            SELECT
                tag.id,
                tag.name,
                tag.active,
                tag.company_id,
                ROW_NUMBER() OVER (PARTITION BY tag.name ORDER BY tag.id) AS row_count
            FROM account_analytic_tag tag
            WHERE tag.active_analytic_distribution = true
        )
        SELECT
            CASE
                WHEN row_count = 1 THEN tag.name
                ELSE CONCAT(tag.name, ' (', tag.id, ')')
            END AS name,
            tag.id,
            tag.active,
            tag.company_id,
            distribution.account_id,
            distribution.percentage
        FROM
            counted_tags tag
            INNER JOIN
                account_analytic_distribution distribution ON tag.id = distribution.tag_id;

        """
        env.cr.execute(sql)
        distribution_by_tag = {}
        distribution_manual_vals = []
        for data in env.cr.dictfetchall():
            tag_key = (data["name"], data["active"], data["company_id"])
            distribution_by_tag.setdefault(tag_key, []).append(data)
        for tag_key, distributions in distribution_by_tag.items():
            tag_name, tag_active, company_id = tag_key
            distribution_manual_val = {
                "name": tag_name,
                "active": tag_active,
                "company_id": company_id or env.company.id,
                "analytic_distribution": {
                    distribution["account_id"]: distribution["percentage"]
                    for distribution in distributions
                },
            }
            distribution_manual_vals.append(distribution_manual_val)
        if distribution_manual_vals:
            env["account.analytic.distribution.manual"].create(distribution_manual_vals)
