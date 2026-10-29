# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # The field is no longer stored: Odoo computes it in SQL
    cr.execute(
        "ALTER TABLE account_analytic_line DROP COLUMN IF EXISTS commercial_partner_id"
    )
    # Odoo keeps the reflection of the dropped foreign key
    cr.execute(
        """
        DELETE FROM ir_model_constraint
        WHERE name = 'account_analytic_line_commercial_partner_id_fkey'
            AND type = 'f'
        """
    )
