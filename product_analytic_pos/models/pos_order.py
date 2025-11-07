from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _get_invoice_lines_values(self, line_values, pos_order_line):
        vals = super()._get_invoice_lines_values(line_values, pos_order_line)
        product = self.env["product.product"].browse(vals["product_id"])
        analytic_accounts = product.product_tmpl_id._get_product_analytic_accounts()
        if analytic_accounts.get("income"):
            vals["analytic_distribution"] = analytic_accounts["income"]
        return vals
