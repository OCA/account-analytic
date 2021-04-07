# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import SUPERUSER_ID
from odoo.api import Environment


_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Set the `other_partner` field on all existing analytic lines.
    :param cr: database cursor
    :param version: str
    :return: None
    """
    _logger.info("Update other_partner field on existing analytic lines.")
    env = Environment(cr, SUPERUSER_ID, {})

    account_move_lines = env["account.move.line"].search([])
    for move_line in account_move_lines:
        other_partner_id = (
            move_line.invoice_id.partner_id.commercial_partner_id.id
        )
        move_line.analytic_line_ids.write(
            {"other_partner_id": other_partner_id}
        )
