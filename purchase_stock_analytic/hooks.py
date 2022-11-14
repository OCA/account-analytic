# Copyright 2022 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, pool):
    cr.execute(
        """
        update stock_move sm
        set analytic_account_id=pol.account_analytic_id
        from purchase_order_line pol
        where sm.purchase_line_id=pol.id and sm.analytic_account_id is null
        """
    )
    cr.execute(
        """
        update account_move_line aml
        set analytic_account_id=sm.analytic_account_id
        from stock_move sm, account_move am
        where am.stock_move_id=sm.id and aml.move_id=am.id and aml.analytic_account_id is null
        returning aml.id
        """
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["account.move.line"].browse(
        _id for _id, in cr.fetchall()
    ).create_analytic_lines()
