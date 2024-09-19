# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Convert company-dependant field to normal."""


def migrate(cr, version):
    cr.execute(
        r"""
        UPDATE account_account AS acc
        SET analytic_policy = prop.value_text
        FROM (
            SELECT
                substring(res_id FROM '\d+')::int AS account_id,
                value_text
            FROM ir_property
            WHERE
                name = 'analytic_policy'
                AND res_id LIKE 'account.account,%'
                AND value_text != 'optional'
        ) AS prop
        WHERE
            acc.id = prop.account_id
        """
    )
    cr.execute(
        """
        DELETE FROM ir_property
        WHERE
            name = 'analytic_policy'
            AND res_id LIKE 'account.account,%'
        """
    )
