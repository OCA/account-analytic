# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env['account.analytic.account']._parent_store_compute()
