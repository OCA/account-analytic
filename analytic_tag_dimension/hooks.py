# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    """Cleanup all dimensions before uninstalling."""
    env["account.analytic.dimension"].search([]).unlink()
