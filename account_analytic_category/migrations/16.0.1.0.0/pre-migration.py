from openupgradelib import openupgrade

models_to_rename = [
    (
        "account.analytic.group",
        "account.analytic.category",
    ),
]


@openupgrade.migrate(use_env=False)
def migrate(cr, version):

    openupgrade.rename_models(cr, models_to_rename)
