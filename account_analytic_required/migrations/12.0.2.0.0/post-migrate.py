from odoo import tools

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.debug('Migrating account.account.type analytic_policy')

    if not tools.column_exists(cr, 'account_account_type', 'analytic_policy'):
        return

    cr.execute("SELECT id FROM res_company")
    company_ids = [d[0] for d in cr.fetchall()]

    cr.execute(
        "SELECT id FROM ir_model_fields WHERE model=%s AND name=%s",
        ('account.account.type', 'property_analytic_policy'))
    [field_id] = cr.fetchone()

    for company_id in company_ids:
        cr.execute("""
            INSERT INTO ir_property (
                name,
                type,
                fields_id,
                company_id,
                res_id,
                value_text
            )
            SELECT
                '{field}',
                'selection',
                {field_id},
                {company_id},
                CONCAT('{model},',id),
                {oldfield}
            FROM {table} t
            WHERE t.{oldfield} IS NOT NULL
            AND NOT EXISTS(
                SELECT 1
                FROM ir_property
                WHERE fields_id={field_id}
                AND company_id={company_id}
                AND res_id=CONCAT('{model},',t.id)
            )
        """.format(
            oldfield='analytic_policy',
            field='property_analytic_policy',
            field_id=field_id,
            company_id=company_id,
            model='account.account.type',
            table='account_account_type',
        ))
