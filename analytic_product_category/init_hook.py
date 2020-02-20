# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.

    Without this script, if a database has a few hundred thousand
    analitic entries, which is not unlikely, the update will take
    at least a few hours.
    """
    store_field_stored_product_category_id(cr)


def store_field_stored_product_category_id(cr):
    """Store product category in the analytic account line."""
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_analytic_line' AND
    column_name='product_category_id'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_analytic_line
            ADD COLUMN product_category_id integer;
            COMMENT ON COLUMN account_analytic_line.product_category_id
            IS 'Product Category';
            """)

    logger.info('Computing field product_category_id on account.analytic.line')

    cr.execute(
        """
        UPDATE account_analytic_line aal
        SET product_category_id = pt.categ_id
        FROM product_product pp
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
        """
    )
