# (c) 2021 Open Source Integrators - Daniel Reis (www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def set_procurement_group_analytic_account(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mos = env["mrp.production"].search([("analytic_account_id", "!=", False)])
    for mo in mos:
        group = mo.move_dest_ids.group_id
        if group.analytic_account_id != mo.analytic_account_id:
            group.write({"analytic_account_id": mo.analytic_account_id.id})
