# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


table_renames = [
    ('account_analytic_plan_instance', 'account_analytic_distribution'),
    ('account_analytic_plan_instance_line',
     'account_analytic_distribution_rule'),
]

column_renames = {
    'account_analytic_plan_instance_line': [
        ('plan_id', 'distribution_id'),
        ('rate', 'percent'),
    ],
    'account_invoice_line': [
        ('analytics_id', 'analytic_distribution_id'),
    ],
    'account_move_line': [
        ('analytics_id', 'analytic_distribution_id'),
    ],
}


models_renames = [
    ('account.analytic.plan.instance', 'account.analytic.distribution'),
    ('account.analytic.plan.instance.line',
     'account.analytic.distribution.rule'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
    openupgrade.rename_models(env.cr, models_renames)
    openupgrade.rename_tables(env.cr, table_renames)
