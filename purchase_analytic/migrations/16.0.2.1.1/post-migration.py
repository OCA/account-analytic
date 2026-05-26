import logging

from openupgradelib import openupgrade  # pylint: disable=W7936

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Check if `project_id` in `purchase_order` exists."
    )
    if openupgrade.column_exists(env.cr, "purchase_order", "project_id"):
        _logger.info(
            "Column `project_id` exists in `purchase_order`."
        )
        if not env["ir.model.fields"].search(
            [("name", "=", "project_id"), ("model", "=", "purchase.order")]
        ):
            _logger.info(
                "Drop `project_id` column from v16 as it will be re-used in v.18 from "
                "the core and it is not present in this environment."
            )
            openupgrade.drop_columns(env.cr, ("purchase_order", "project_id"))
