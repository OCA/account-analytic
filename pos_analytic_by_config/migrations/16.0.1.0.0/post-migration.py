# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    For every company:
    - Check if there are analytic accounts configured in that company's pos configs
    - If so, create a new analytic plan (Stores)
    - Assign that analytic plan to the pos configs analytic accounts
    - Create a miscellaneous applicability rule that is mandatory
    - Create an analytic distribution model for each pos_config / analytic account
    """
    env.cr.execute(
        """
        SELECT id, account_analytic_id FROM pos_config
        WHERE account_analytic_id IS NOT NULL
    """
    )
    pos_configs_dict = {
        env["pos.config"].browse(id): env["analytic.account"].browse(aa_id)
        for id, aa_id, *_ in env.cr.fetchall()
    }
    pos_configs = env["pos.config"].browse([pc.id for pc in pos_configs_dict.keys()])
    for company in pos_configs.company_id:
        company_configs = pos_configs.filtered(lambda x: x.company_id == company)
        default_account_revenue = env["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("account_type", "=", "income"),
                (
                    "id",
                    "!=",
                    company.account_journal_early_pay_discount_gain_account_id.id,
                ),
            ],
            limit=1,
        )
        analytic_plan = env["account.analytic.plan"].create(
            {
                "name": "Stores",
                "default_applicability": "optional",
                "company_id": company.id,
            }
        )
        env["account.analytic.applicability"].create(
            {
                "business_domain": "general",
                "analytic_plan_id": analytic_plan.id,
                "applicability": "mandatory",
            }
        )
        for config in company_configs:
            analytic_account = pos_configs_dict[config]
            analytic_account.analytic_plan_id = analytic_plan.id
            env["account.analytic.distribution.model"].create(
                {
                    "account_prefix": default_account_revenue.code[:3],
                    "pos_config_id": config.id,
                    "analytic_distribution": {analytic_account.id: 100},
                }
            )
