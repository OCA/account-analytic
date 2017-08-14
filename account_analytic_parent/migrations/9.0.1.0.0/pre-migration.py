# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    """Restores visibility of accounts of type='view'. They are not exactly
    the same as parent accounts, but both values are very tighted"""
    openupgrade.logged_query(
        cr,
        """UPDATE account_analytic_account SET account_type='normal'
        WHERE %s = 'view' AND %s NOT IN ('cancelled', 'close')
        """ % (
            openupgrade.get_legacy_name('type'),
            openupgrade.get_legacy_name('state'),
        )
    )
