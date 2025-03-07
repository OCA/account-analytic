from odoo import models, api
from odoo.addons.product_analytic.models.account_invoice import INV_TYPE_MAP
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging
_logger = logging.getLogger(__name__)



class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def cron_update_analytic_account(self, from_date="2024-01-01 00:00:00", limit=300):
        """Update analytic accounts for move lines of invoices.
        based on the expense and income accounts of the product or category.
        """
        # Check from_date from config parameter
        from_date = self.env['ir.config_parameter'].sudo().get_param(
            'update_analytic_account_from_date', from_date)
        args = [
            ('invoice_id', '!=', False),
            ('product_id', '!=', False),
            ('analytic_account_id', '=', False),
            ('date', '>=', from_date)
        ]
        lines = self.env["account.move.line"].search(args, order='date', limit=limit)
        if not lines:
            return
        # Loop through each line and update the analytic account
        # base on INV_TYPE_MAP from product_analytic/models/account_invoice.py
        for line in lines:
            inv_type = line.invoice_id.type
            if inv_type not in INV_TYPE_MAP:
                continue
            ana_accounts = line.product_id.product_tmpl_id._get_product_analytic_accounts()
            ana_account = ana_accounts[INV_TYPE_MAP[inv_type]]
            if ana_account:
                _logger.info("=====================================")
                _logger.info(
                    f"Updating analytic account for line {line.id} (#Move ID: {line.move_id.id}) "
                    f"with product {line.product_id.name} "
                    f"and invoice type {inv_type}: {ana_account.name}")
                line.analytic_account_id = ana_account.id
        # Update the last processed date in config parameter
        last_date = lines[-1].date.strftime(DTF)
        self.env['ir.config_parameter'].sudo().set_param(
            'update_analytic_account_from_date', last_date)
