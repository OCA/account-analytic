from odoo.tools.sql import column_exists


def migrate(cr, version):
    """Populate analytic distribution values from the old analytic account"""
    if column_exists(cr, "purchase_request", "analytic_distribution"):
        return
    cr.execute(
        """
        ALTER TABLE purchase_request ADD COLUMN analytic_distribution jsonb;
        update purchase_request set analytic_distribution =
        json_build_object(analytic_account_id::varchar, 100.0)
        where analytic_account_id is not null;
        """
    )
