# Copyright 2026 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from psycopg2 import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    cr = env.cr

    _logger.info("Creating source move analytic info columns.")
    _create_columns(cr)

    analytic_field_names = _get_analytic_account_column_names(cr)

    _logger.info(
        "Backfilling source move analytic info using SQL. Analytic columns: %s",
        ", ".join(analytic_field_names),
    )

    _sql_backfill_source_move_currency_id(cr)
    _sql_backfill_source_move_amounts(cr)

    if analytic_field_names:
        _sql_backfill_analytic_percentage(cr, analytic_field_names)
    else:
        _logger.warning(
            "No analytic account columns found on account_analytic_line. "
            "analytic_percentage will be set to 0.0."
        )
        cr.execute(
            """
            UPDATE account_analytic_line
               SET analytic_percentage = 0.0
             WHERE analytic_percentage IS NULL
            """
        )

    _sql_backfill_source_move_total_analytic_percentage(cr)

    _logger.info("Finished pre-init source move analytic info backfill.")


def _create_columns(cr):
    cr.execute(
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS source_move_currency_id integer
        """
    )
    cr.execute(
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS analytic_percentage double precision
        """
    )
    cr.execute(
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS source_move_line_base_amount numeric
        """
    )
    cr.execute(
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS source_move_base_amount numeric
        """
    )
    cr.execute(
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS source_move_total_analytic_percentage double precision
        """
    )


def _get_analytic_account_column_names(cr):
    cr.execute(
        """
        SELECT c.column_name
          FROM information_schema.columns c
          JOIN ir_model_fields f
            ON f.name = c.column_name
         WHERE c.table_name = 'account_analytic_line'
           AND f.model = 'account.analytic.line'
           AND f.ttype = 'many2one'
           AND f.relation = 'account.analytic.account'
           AND (
                c.column_name = 'account_id'
                OR c.column_name LIKE 'x_plan%%'
           )
         ORDER BY c.column_name
        """
    )
    return [row[0] for row in cr.fetchall()]


def _sql_backfill_source_move_currency_id(cr):
    cr.execute(
        """
        UPDATE account_analytic_line aal
           SET source_move_currency_id = COALESCE(
                am.currency_id,
                aml.currency_id,
                aal.currency_id,
                (
                    SELECT rc.currency_id
                      FROM res_company rc
                     WHERE rc.id = aal.company_id
                     LIMIT 1
                )
           )
          FROM account_move_line aml
          JOIN account_move am
            ON am.id = aml.move_id
         WHERE aal.move_line_id = aml.id
        """
    )


def _sql_backfill_source_move_amounts(cr):
    cr.execute(
        """
        UPDATE account_analytic_line aal
           SET source_move_line_base_amount =
                CASE
                    WHEN base.line_amount IS NULL THEN 0.0
                    WHEN base.line_amount = 0.0 THEN 0.0
                    WHEN aal.amount IS NULL OR aal.amount = 0.0 THEN base.line_amount
                    WHEN aal.amount > 0.0 THEN ABS(base.line_amount)
                    ELSE -ABS(base.line_amount)
                END,
               source_move_base_amount =
                CASE
                    WHEN base.move_amount IS NULL THEN 0.0
                    WHEN base.move_amount = 0.0 THEN 0.0
                    WHEN aal.amount IS NULL OR aal.amount = 0.0 THEN base.move_amount
                    WHEN aal.amount > 0.0 THEN ABS(base.move_amount)
                    ELSE -ABS(base.move_amount)
                END
          FROM (
                SELECT
                    aml.id AS move_line_id,
                    CASE
                        WHEN am.move_type IN (
                            'out_invoice',
                            'out_refund',
                            'in_invoice',
                            'in_refund',
                            'out_receipt',
                            'in_receipt'
                        )
                        THEN COALESCE(
                            NULLIF(aml.price_subtotal, 0.0),
                            NULLIF(aml.amount_currency, 0.0),
                            aml.balance,
                            0.0
                        )
                        ELSE COALESCE(
                            NULLIF(aml.price_total, 0.0),
                            NULLIF(aml.amount_currency, 0.0),
                            aml.balance,
                            0.0
                        )
                    END AS line_amount,
                    CASE
                        WHEN am.move_type IN (
                            'out_invoice',
                            'out_refund',
                            'in_invoice',
                            'in_refund',
                            'out_receipt',
                            'in_receipt'
                        )
                        THEN COALESCE(am.amount_untaxed, 0.0)
                        ELSE COALESCE(
                            NULLIF(am.amount_total, 0.0),
                            NULLIF(aml.amount_currency, 0.0),
                            aml.balance,
                            0.0
                        )
                    END AS move_amount
                FROM account_move_line aml
                JOIN account_move am
                  ON am.id = aml.move_id
          ) AS base
         WHERE aal.move_line_id = base.move_line_id
        """
    )


def _sql_backfill_analytic_percentage(cr, analytic_field_names):
    analytic_id_values = [
        sql.SQL("aal.{field_name}::text").format(field_name=sql.Identifier(field_name))
        for field_name in analytic_field_names
    ]

    values_sql = sql.SQL(", ").join(
        sql.SQL("({value})").format(value=value) for value in analytic_id_values
    )

    query = sql.SQL(
        """
        WITH aal_combination AS (
            SELECT
                aal.id AS analytic_line_id,
                aal.move_line_id AS move_line_id,
                string_agg(
                    v.account_id,
                    ','
                    ORDER BY v.account_id::integer
                ) AS account_key
            FROM account_analytic_line aal
            CROSS JOIN LATERAL (
                VALUES {values_sql}
            ) AS v(account_id)
            WHERE v.account_id IS NOT NULL
              AND aal.move_line_id IS NOT NULL
            GROUP BY aal.id, aal.move_line_id
        ),
        distribution_combination AS (
            SELECT
                aml.id AS move_line_id,
                string_agg(
                    split_accounts.account_id,
                    ','
                    ORDER BY split_accounts.account_id::integer
                ) AS account_key,
                MAX(distribution.value::text::numeric) AS percentage
            FROM account_move_line aml
            CROSS JOIN LATERAL jsonb_each(
                aml.analytic_distribution::jsonb
            ) AS distribution(key, value)
            CROSS JOIN LATERAL regexp_split_to_table(
                distribution.key,
                ','
            ) AS split_accounts(account_id)
            WHERE aml.analytic_distribution IS NOT NULL
            GROUP BY aml.id, distribution.key
        ),
        matched_percentage AS (
            SELECT
                ac.analytic_line_id,
                dc.percentage
            FROM aal_combination ac
            JOIN distribution_combination dc
              ON dc.move_line_id = ac.move_line_id
             AND dc.account_key = ac.account_key
        )
        UPDATE account_analytic_line aal
           SET analytic_percentage = COALESCE(mp.percentage, 0.0)
          FROM matched_percentage mp
         WHERE aal.id = mp.analytic_line_id
        """
    ).format(values_sql=values_sql)

    cr.execute(query)

    cr.execute(
        """
        UPDATE account_analytic_line
           SET analytic_percentage = 0.0
         WHERE analytic_percentage IS NULL
        """
    )


def _sql_backfill_source_move_total_analytic_percentage(cr):
    cr.execute(
        """
        UPDATE account_analytic_line aal
           SET source_move_total_analytic_percentage =
                CASE
                    WHEN COALESCE(aal.source_move_base_amount, 0.0) = 0.0 THEN 0.0
                    ELSE
                        aal.analytic_percentage
                        * aal.source_move_line_base_amount
                        / aal.source_move_base_amount
                END
         WHERE aal.move_line_id IS NOT NULL
        """
    )
