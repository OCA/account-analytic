# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api, tools

# metadata for all models related to account_analytic_tag(m2m)
# add more models if needed
RELATION_M2M_INFO = {
    "account_analytic_tag_account_asset_profile_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "account_asset_profile",
        "column2": "account_asset_profile_id",
    },
    "account_analytic_tag_hr_expense_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "hr_expense",
        "column2": "hr_expense_id",
    },
    "account_reconcile_model_second_analytic_tag_rel": {
        "table2": "account_reconcile_model",
        "column2": "account_reconcile_model_id",
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
    },
    "hr_timesheet_switch_line_tag_rel": {
        "table2": "hr_timesheet_switch",
        "column2": "line_id",
        "table1": "account_analytic_tag",
        "column1": "tag_id",
    },
    "account_analytic_tag_sale_order_line_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "sale_order_line",
        "column2": "sale_order_line_id",
    },
    "account_reconcile_model_analytic_tag_rel": {
        "table2": "account_reconcile_model_line",
        "column2": "account_reconcile_model_line_id",
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
    },
    "account_analytic_tag_mis_report_instance_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "mis_report_instance",
        "column2": "mis_report_instance_id",
    },
    "account_analytic_tag_account_move_line_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "account_move_line",
        "column2": "account_move_line_id",
    },
    "account_analytic_tag_mis_report_instance_period_rel": {
        "table2": "mis_report_instance_period",
        "column2": "mis_report_instance_period_id",
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
    },
    "account_analytic_tag_general_ledger_report_wizard_rel": {
        "table2": "general_ledger_report_wizard",
        "column2": "general_ledger_report_wizard_id",
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
    },
    "account_analytic_default_account_analytic_tag_rel": {
        "table2": "account_analytic_default",
        "column2": "account_analytic_default_id",
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
    },
    "account_analytic_tag_purchase_order_line_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "purchase_order_line",
        "column2": "purchase_order_line_id",
    },
    "account_analytic_tag_account_asset_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "account_asset",
        "column2": "account_asset_id",
    },
    "account_analytic_tag_project_task_stock_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "project_task",
        "column2": "project_task_id",
    },
    "account_analytic_tag_project_task_rel": {
        "table1": "account_analytic_tag",
        "column1": "account_analytic_tag_id",
        "table2": "project_task",
        "column2": "project_task_id",
    },
    "account_analytic_line_tag_rel": {
        "table2": "account_analytic_line",
        "column2": "line_id",
        "table1": "account_analytic_tag",
        "column1": "tag_id",
    },
}


def post_init_hook(cr, registry):
    if tools.table_exists(cr, "account_analytic_tag"):
        env = api.Environment(cr, SUPERUSER_ID, {})
        DistributionManual = env["account.analytic.distribution.manual"]
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
        for data in env.cr.dictfetchall():
            tag_key = (data["id"], data["name"], data["active"], data["company_id"])
            distribution_by_tag.setdefault(tag_key, []).append(data)
        distribution_map = {}
        all_tag_ids = []
        for tag_key, distributions in distribution_by_tag.items():
            tag_id, tag_name, tag_active, company_id = tag_key
            distribution_manual_val = {
                "name": tag_name,
                "active": tag_active,
                "company_id": company_id or env.company.id,
                "analytic_distribution": {
                    distribution["account_id"]: distribution["percentage"]
                    for distribution in distributions
                },
            }
            new_distribution = DistributionManual.create(distribution_manual_val)
            distribution_map[tag_id] = new_distribution
            all_tag_ids.append(tag_id)
        # Update references in all models related to account_analytic_tag(m2m)
        for table_m2m, info in RELATION_M2M_INFO.items():
            column1 = info["column1"]
            table2 = info["table2"]
            column2 = info["column2"]
            res_model_name = table2.replace("_", ".")
            if (
                res_model_name in env
                and "manual_distribution_id" in env[res_model_name]._fields
            ):
                sql = f"""
                SELECT {column1}, {column2}
                FROM {table_m2m}
                WHERE {column1} IN %s
                """
                env.cr.execute(sql, (tuple(all_tag_ids),))
                for tag_id, res_id in env.cr.fetchall():
                    env.cr.execute(
                        f"""
                        UPDATE {table2}
                        SET manual_distribution_id = %s
                        WHERE id = %s
                        """,
                        (distribution_map[tag_id].id, res_id),
                    )
