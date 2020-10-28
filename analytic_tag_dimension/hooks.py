# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    """Cleanup all dimensions before uninstalling."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["account.analytic.dimension"].search([]).unlink()
