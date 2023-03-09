# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(
        "Add value 'stock_account_line_debit' company on upgrade to 15.0.1.1.0"
    )
    env.cr.execute("ALTER TABLE res_company ADD COLUMN stock_account_line_debit bool;")
