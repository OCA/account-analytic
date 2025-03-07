from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _prepare_analytic_account(self, line):
        analytic_accounts = line.product_id.product_tmpl_id._get_product_analytic_accounts()
        if analytic_accounts.get("income"):
            return analytic_accounts['income'].id
        return super(PosOrder, self)._prepare_analytic_account(line)

    @api.model
    def cron_update_analytic_account(self, from_date="2024-01-01 00:00:00", limit=100):
        last_id = self.env[
            'ir.config_parameter'].sudo().get_param(
            'update_analytic_account_last_id')
        args = [('account_move', '!=', False)]
        if last_id:
            args.append(('id', '>', int(last_id)))
        else:
            args.append(('date_order', '>=', from_date))
        orders = self.search(args, order='id', limit=limit)

        for order in orders:
            for line in order.account_move.line_ids:
                if not line.product_id or line.credit <= 0 or line.analytic_account_id:
                    continue
                income_account = False
                if line.product_id.property_account_income_id:
                    income_account = line.product_id.property_account_income_id.id
                elif line.product_id.categ_id.property_account_income_categ_id:
                    income_account = line.product_id.categ_id.property_account_income_categ_id.id
                if not income_account or line.account_id.id != income_account:
                    continue
                analytic_accounts = line.product_id.product_tmpl_id._get_product_analytic_accounts()
                if analytic_accounts.get("income"):
                    line.analytic_account_id = analytic_accounts['income']

        if orders:
            self.env['ir.config_parameter'].sudo().set_param(
                'update_analytic_account_last_id', orders[-1].id)
